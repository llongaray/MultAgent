"""Isolated, authenticated privilege-request protocol; no LLM-held administrator rights."""
from .broker import BrokerDenied, BrokerTicket, PrivilegeBroker
from .ipc import BrokerIPC
__all__ = ["BrokerDenied", "BrokerTicket", "PrivilegeBroker", "BrokerIPC"]
