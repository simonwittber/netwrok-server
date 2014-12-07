from collections import defaultdict


class PresenceRegister:

    def __init__(self):
        self.register = defaultdict(set)
        self.present = set()

    def notify(self, event, listener_id, id):
        pass

    def add(self, arrived_id):
        self.present.add(arrived_id)
        for listener_id in self.register[arrived_id]:
            self.notify('arrive', listener_id, arrived_id)

    def remove(self, left_id):
        self.present.remove(left_id)
        for listener_id in self.register[left_id]:
            self.notify('leave', listener_id, left_id)

    def register_interest(self, listener_id, id):
        self.register[id].add(listener_id)
        if id in self.present:
            self.notify('arrive', listener_id, id)

