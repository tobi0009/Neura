import torch
from sentence_transformers import util
from .models import KnowledgeBaseEntry
from .utils import get_embedding

def find_best_match(assistant, query: str, threshold: float = 0.6):
    # Convert query to embedding
    query_embedding = get_embedding(query)

    entries = KnowledgeBaseEntry.objects.filter(assistant=assistant, embedding__isnull=False)

    if not entries:
        return None, 0.0

    best_entry = None
    best_score = 0.0

    for entry in entries:
        score = util.cos_sim(torch.tensor(query_embedding), torch.tensor(entry.embedding))[0][0].item()
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_score >= threshold:
        return best_entry, best_score

    return None, best_score


def find_top_matches(assistant, query: str, top_k: int = 5):
    query_embedding = get_embedding(query)
    entries = KnowledgeBaseEntry.objects.filter(assistant=assistant, embedding__isnull=False)

    if not entries:
        return []

    scored_entries = []
    for entry in entries:
        score = util.cos_sim(torch.tensor(query_embedding), torch.tensor(entry.embedding))[0][0].item()
        scored_entries.append((entry, score))

    # Sort by highest score
    scored_entries.sort(key=lambda x: x[1], reverse=True)

    # Return top_k entries with scores
    return scored_entries[:top_k]


def find_top_matches_from_entries(entries, query: str, top_k: int = 5):
    """
    Same as find_top_matches but takes entries as parameter instead of querying database
    """
    query_embedding = get_embedding(query)
    
    if not entries:
        return []

    scored_entries = []
    for entry in entries:
        score = util.cos_sim(torch.tensor(query_embedding), torch.tensor(entry.embedding))[0][0].item()
        scored_entries.append((entry, score))

    # Sort by highest score
    scored_entries.sort(key=lambda x: x[1], reverse=True)

    # Return top_k entries with scores
    return scored_entries[:top_k]

