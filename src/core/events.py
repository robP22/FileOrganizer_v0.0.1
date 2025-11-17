from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class Event:
    """ Base event class for all application events """
    type: str
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class EventBus:
    """ Central event bus for decoupled communication between components. """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Event], None]):
        """ Subscribe to an event of type . """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: Dict[str, Any] = None):
        """ Publish event to all subscribers. """
        event = Event(type=event_type, data=data or {})
        if event.type in self.subscribers:
            for callback in self.subscribers[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event handler for {event_type}: {e}")

    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]):
        """ Unsubscribe from an event type. """
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
            except ValueError:
                pass  # Callback not found, ignore

event_bus = EventBus() # Global instance for application-wide use