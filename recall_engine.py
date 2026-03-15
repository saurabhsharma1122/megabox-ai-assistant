# recall_engine.py
"""
Relevance-scored memory retrieval across all Megabox memory sources.

Architecture
------------
Retrieval is a three-stage pipeline:

  1. Collect  — gather raw entries from all memory files
  2. Score    — rank by relevance (query match) × importance (content type)
                with a small recency bonus
  3. Surface  — deduplicate, cap, persist high-value results to recall file

Scoring formula
---------------
  final_score = relevance × importance_weight + recency_bonus

  relevance       = F1-overlap(query_tokens, entry_tokens)
                    symmetric — not biased by query length or entry length

  importance_weight = 0.3 – 1.0 based on content category
                      personal facts > preferences > opinions >
                      experiences > general > (noise skipped entirely)

  recency_bonus   = up to +0.12, exponential decay over 60 days
                    smooth — no hard cliff

Public API
----------
  search_memory(query, top_n)    → list of relevant strings
  build_recall_context(query)    → prompt-ready block for brain.py
"""

import json
import os
import re
import time
from typing import Dict, List, Optional, Set, Tuple

# ──────────────────────────────────────────────────────────────
# File paths
# ──────────────────────────────────────────────────────────────

LONG_MEMORY = "long_memory.json"
MEMORY_FILE = "memory.json"
RECALL_FILE = "mind/recall_memory.json"

# Maximum entries kept in the recall persistence file.
# Pruned by importance score (not FIFO) so valuable memories survive longer.
_RECALL_CAP = 60

# ──────────────────────────────────────────────────────────────
# Stop words — words that carry no retrieval signal
# ──────────────────────────────────────────────────────────────

_STOP_WORDS: Set[str] = {
    "i", "me", "my", "we", "us", "our", "you", "your",
    "a", "an", "the", "this", "that", "these", "those",
    "is", "are", "was", "were", "be", "been", "being",
    "am", "will", "would", "could", "should", "can", "may", "might",
    "have", "has", "had", "do", "did", "does",
    "it", "its", "in", "on", "at", "to", "for", "of", "and",
    "or", "but", "so", "if", "as", "with", "by", "from",
    "not", "no", "yes", "just", "also", "very", "quite",
    "he", "she", "they", "him", "her", "them",
    "what", "when", "where", "who", "how", "why",
    "then", "than", "there", "here", "now", "up", "out",
    "about", "into", "through", "more", "some", "any",
}

# ──────────────────────────────────────────────────────────────
# Noise patterns — entries matching these are skipped entirely
# before scoring.  They contain no learnable content.
# ──────────────────────────────────────────────────────────────

_NOISE_RE = re.compile(
    r"^\s*(ok|okay|sure|fine|got it|alright|right|yep|nope|"
    r"hello|hi|hey|bye|goodbye|thanks|thank you|"
    r"no|yes|yeah|nah|hmm|oh|ah|hm|cool|nice|great|wow|"
    r"really|seriously|interesting|awesome|perfect)\s*[!?.]*\s*$",
    re.IGNORECASE,
)

# ──────────────────────────────────────────────────────────────
# Importance classification
#
# Each category has a weight used to amplify (or suppress) the
# relevance score.  Higher weight = surfaces more readily.
# ──────────────────────────────────────────────────────────────

_IMPORTANCE: Dict[str, float] = {
    "personal_fact": 1.00,   # name, age, location, occupation
    "preference":    0.90,   # I like / love / enjoy / hate / prefer
    "opinion":       0.75,   # I think / believe / feel / find
    "experience":    0.65,   # I went / tried / did / used / made
    "general":       0.40,   # everything that passed noise filter
}

# Detection patterns, ordered from most to least specific.
# Each entry: (category_key, compiled_regex)
_IMPORTANCE_PATTERNS: List[Tuple[str, re.Pattern]] = [
    (
        "personal_fact",
        re.compile(
            r"\b(my name is|i(?:'m| am) (?:called|named)|"
            r"i(?:'m| am) \d{1,2} years|"
            r"i(?:'m| am) from|i live in|i(?:'m| am) based in|"
            r"i(?:'m| am) (?:a|an) \w+er\b|"          # i'm a developer
            r"i work as|my (?:age|job|occupation|location|hometown))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "preference",
        re.compile(
            r"\b(i (?:like|love|enjoy|hate|dislike|prefer|can't stand|"
            r"really like|really love|always like|always love)|"
            r"my (?:favourite|favorite)|i(?:'m| am) into|"
            r"i(?:'m| am) a fan of|i(?:'m| am) not a fan)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "opinion",
        re.compile(
            r"\b(i (?:think|believe|feel|find|reckon|guess|suppose)|"
            r"in my opinion|i(?:'m| am) (?:sure|certain|convinced))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "experience",
        re.compile(
            r"\b(i (?:went|tried|used|made|built|created|played|read|"
            r"watched|visited|learned|started|finished|worked on|"
            r"bought|got|saw|heard|ate|cooked))\b",
            re.IGNORECASE,
        ),
    ),
]

# ──────────────────────────────────────────────────────────────
# Topic expansion map
#
# Bridges semantically related terms so that a query about
# "food" also matches entries about "vegetarian", "spicy", etc.
# Keys are canonical topics; values are related keywords that
# will be added to the query token set when the key is present.
# ──────────────────────────────────────────────────────────────

_TOPIC_EXPANSION: Dict[str, List[str]] = {
    "music":       ["song", "songs", "artist", "album", "band", "playlist",
                    "genre", "rock", "pop", "jazz", "classical", "rap", "hip"],
    "food":        ["eat", "eating", "diet", "vegetarian", "vegan", "spicy",
                    "meal", "cooking", "recipe", "cuisine", "restaurant"],
    "coding":      ["code", "python", "program", "script", "developer",
                    "programming", "software", "algorithm", "function", "bug"],
    "work":        ["job", "career", "office", "company", "project",
                    "profession", "engineer", "developer", "designer"],
    "sports":      ["exercise", "gym", "workout", "fitness", "run", "running",
                    "football", "cricket", "tennis", "yoga", "training"],
    "movies":      ["film", "watch", "cinema", "series", "show", "netflix",
                    "episode", "director", "actor"],
    "books":       ["read", "reading", "novel", "author", "story", "chapter",
                    "literature", "fiction", "nonfiction"],
    "games":       ["gaming", "play", "playing", "game", "steam", "console",
                    "controller", "level", "rpg"],
    "travel":      ["trip", "vacation", "country", "city", "visit", "visited",
                    "abroad", "flight", "tour"],
    "health":      ["doctor", "medicine", "diet", "sleep", "stress",
                    "mental", "exercise", "illness", "therapy"],
    "preferences": ["like", "love", "enjoy", "hate", "prefer", "favourite",
                    "favorite", "choice"],
}


# ──────────────────────────────────────────────────────────────
# Storage helpers
# ──────────────────────────────────────────────────────────────

def _load(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def _save(path: str, data) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# ──────────────────────────────────────────────────────────────
# Tokenization and expansion
# ──────────────────────────────────────────────────────────────

def _tokenize(text: str) -> Set[str]:
    """Extract meaningful words, strip stop words and short tokens."""
    words = re.findall(r"\b[a-z]{2,}\b", text.lower())
    return {w for w in words if w not in _STOP_WORDS}


def _expand_query(tokens: Set[str]) -> Set[str]:
    """
    Add semantically related keywords for recognised topic tokens.
    Example: {"music", "like"} → adds rock, pop, song, songs, ...
    This bridges entries that use different but related vocabulary.
    """
    expanded = set(tokens)
    for topic, related in _TOPIC_EXPANSION.items():
        if topic in tokens:
            expanded.update(related)
        # Also expand if any related word appears in the query
        elif tokens & set(related):
            expanded.add(topic)
            expanded.update(related)
    return expanded


# ──────────────────────────────────────────────────────────────
# Importance classification
# ──────────────────────────────────────────────────────────────

def _classify_importance(text: str) -> Tuple[str, float]:
    """
    Return (category_name, weight) for a memory entry.
    Returns ("noise", 0.0) for entries that should be skipped entirely.
    """
    if not text or len(text.split()) < 2:
        return ("noise", 0.0)

    if _NOISE_RE.match(text):
        return ("noise", 0.0)

    for category, pattern in _IMPORTANCE_PATTERNS:
        if pattern.search(text):
            return (category, _IMPORTANCE[category])

    return ("general", _IMPORTANCE["general"])


# ──────────────────────────────────────────────────────────────
# Scoring
# ──────────────────────────────────────────────────────────────

def _f1_overlap(query_tokens: Set[str], entry_tokens: Set[str]) -> float:
    """
    Symmetric F1-based overlap: 2 * |intersection| / (|query| + |entry|).

    Unlike simple precision (overlap / query_size), this is not fooled
    by very short queries or very short entries.

    Returns 0.0 if either token set is empty.
    """
    if not query_tokens or not entry_tokens:
        return 0.0

    intersection = len(query_tokens & entry_tokens)
    if intersection == 0:
        return 0.0

    return (2.0 * intersection) / (len(query_tokens) + len(entry_tokens))


def _recency_bonus(created_at: float, max_bonus: float = 0.12, half_life_days: float = 20.0) -> float:
    """
    Exponential decay recency bonus.

    max_bonus   = maximum contribution at age 0
    half_life   = days until bonus halves (smooth, no hard cliff)

    At 0 days old  → +0.12
    At 20 days old → +0.06
    At 40 days old → +0.03
    At 80 days old → +0.0075  (effectively negligible)
    """
    if not created_at:
        return 0.0
    age_days = max(0.0, (time.time() - created_at) / 86_400)
    return round(max_bonus * (0.5 ** (age_days / half_life_days)), 4)


def _score_entry(
    query_tokens: Set[str],
    entry_text:   str,
    created_at:   float = 0.0,
) -> float:
    """
    Compute final retrieval score for a single memory entry.

    final_score = f1_overlap × importance_weight + recency_bonus

    Returns 0.0 for noise entries (they are skipped before scoring
    in the caller, but this is a safe fallback).
    """
    category, importance_weight = _classify_importance(entry_text)
    if category == "noise":
        return 0.0

    entry_tokens = _tokenize(entry_text)
    relevance    = _f1_overlap(query_tokens, entry_tokens)

    if relevance == 0.0:
        return 0.0

    recency = _recency_bonus(created_at)
    return round(relevance * importance_weight + recency, 4)


# ──────────────────────────────────────────────────────────────
# Memory collection
# ──────────────────────────────────────────────────────────────

def _collect_all_memories() -> List[Dict]:
    """
    Gather raw entries from all known memory files.

    Each returned entry is a dict:
        { "text": str, "source": str, "created_at": float }

    Rules:
    - long_memory.json sections: both string and dict items are supported.
    - memory.json conversation history: ONLY user turns are indexed.
      Agent turns are Megabox's own words, not facts about the user,
      and should not be retrieved as user memories.
    - Entries shorter than 3 words are discarded before returning.
    """
    entries: List[Dict] = []

    # ── long_memory.json ─────────────────────────────────────
    long_mem = _load(LONG_MEMORY, {})
    for section_name, section in long_mem.items():
        if not isinstance(section, list):
            continue
        for item in section:
            if isinstance(item, str):
                text = item.strip()
                ts   = 0.0
            elif isinstance(item, dict):
                text = (
                    item.get("text")
                    or item.get("content")
                    or item.get("message", "")
                ).strip()
                ts = item.get("created_at", 0.0)
            else:
                continue

            if text and len(text.split()) >= 3:
                entries.append({
                    "text":       text,
                    "source":     section_name,
                    "created_at": ts,
                })

    # ── memory.json (conversation history) ───────────────────
    # Only user turns — agent turns are Megabox's own words.
    for turn in _load(MEMORY_FILE, []):
        if not isinstance(turn, dict):
            continue
        user_text = turn.get("user", "").strip()
        if user_text and len(user_text.split()) >= 3:
            entries.append({
                "text":       user_text,
                "source":     "conversation",
                "created_at": turn.get("created_at", 0.0),
            })

    return entries


# ──────────────────────────────────────────────────────────────
# Recall file persistence
# ──────────────────────────────────────────────────────────────

def _persist_recall(new_entries: List[Tuple[float, str]]) -> None:
    """
    Merge new high-scoring entries into the recall file.

    Deduplicates, then sorts all stored entries by importance score
    and keeps only the top _RECALL_CAP.  This means genuinely valuable
    memories survive longer than trivial ones (unlike a FIFO cap).
    """
    if not new_entries:
        return

    recall   = _load(RECALL_FILE, {"important_memories": []})
    existing = {e["text"] for e in recall["important_memories"]
                if isinstance(e, dict)}

    for score, text in new_entries:
        if text not in existing:
            recall["important_memories"].append({
                "text":       text,
                "score":      score,
                "saved_at":   time.time(),
            })
            existing.add(text)

    # Sort by score descending, keep top _RECALL_CAP
    recall["important_memories"].sort(
        key=lambda e: e.get("score", 0.0) if isinstance(e, dict) else 0.0,
        reverse=True,
    )
    recall["important_memories"] = recall["important_memories"][:_RECALL_CAP]

    _save(RECALL_FILE, recall)


# ──────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────

def search_memory(query: str, top_n: int = 4) -> List[str]:
    """
    Search all memory sources for entries relevant to the query.

    Pipeline:
      1. Tokenise and expand the query with related keywords.
      2. Score each memory entry (noise entries score 0.0 and are skipped).
      3. Sort by score, deduplicate, return top_n.
      4. Persist high-scoring results to the recall file.

    Returns a list of plain text strings, best match first.
    """
    base_tokens     = _tokenize(query)
    expanded_tokens = _expand_query(base_tokens)

    if not expanded_tokens:
        return []

    scored: List[Tuple[float, str]] = []

    for entry in _collect_all_memories():
        # Pre-filter: skip noise before calling the scorer
        category, _ = _classify_importance(entry["text"])
        if category == "noise":
            continue

        score = _score_entry(expanded_tokens, entry["text"], entry.get("created_at", 0.0))
        if score > 0.0:
            scored.append((score, entry["text"]))

    # Sort descending, deduplicate, take top_n
    seen:   Set[str]  = set()
    ranked: List[str] = []

    for score, text in sorted(scored, key=lambda x: x[0], reverse=True):
        if text not in seen:
            seen.add(text)
            ranked.append(text)
        if len(ranked) >= top_n:
            break

    # Persist the top results
    top_scored = [(s, t) for s, t in scored if t in seen]
    _persist_recall(top_scored)

    return ranked


def build_recall_context(query: str, top_n: int = 3) -> str:
    """
    Build a compact memory block ready for prompt injection in brain.py.
    Returns an empty string when no relevant memories are found,
    so callers can safely do:

        block = build_recall_context(user_input)
        if block:
            context += block
    """
    results = search_memory(query, top_n=top_n)
    if not results:
        return ""

    lines = "\n".join(f"- {r}" for r in results)
    return (
        "Relevant past context "
        "(use naturally if helpful — do not force or announce):\n"
        f"{lines}\n"
    )