class Peer:

    def __init__(self, peer_data: bytearray):
        self.ip = ".".join([str(n) for n in peer_data[:4]])
        self.port = (peer_data[4] << 8) | peer_data[5]

    def __repr__(self):
        return f"""
            Ip: {self.ip}
            Port: {self.port}
        """


class TrackerResponse:

    def __init__(self, tracker_response_dict: dict):
        if "failure reason" in tracker_response_dict:
            self.failure_reason = tracker_response_dict["failure reason"]
        else:
            self.failure_reason = None
            self.interval = tracker_response_dict["interval"]
            self.peers = [Peer(tracker_response_dict["peers"][n:n+6]) for n in range(0, len(tracker_response_dict["peers"]), 6)]

    def __repr__(self):
        if self.failure_reason:
            return self.failure_reason

        return f"""
            Interval: {self.interval}
            Peers: {self.peers}
        """