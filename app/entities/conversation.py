"""Domain entity: ConversationSummary.

A per-peer summary of a user's conversations: the other party, the last
message exchanged and the number of unread messages from that peer.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConversationSummary:
    """Summary of a 1:1 conversation from one user's point of view."""

    peer_id: int
    peer_name: str
    last_message: str
    last_at: datetime
    unread: int
