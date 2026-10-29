from typing import List, Tuple

from vidur.entities import Request
from vidur.scheduler.global_scheduler.base_global_scheduler import BaseGlobalScheduler


class LOTGlobalScheduler(BaseGlobalScheduler):
    """Least outstanding tokens (LOT): send each request to the replica with
    the least work in flight, measured in tokens.

    A request's work is the tokens it still has to process:
        request.total_tokens - request.num_processed_tokens
    (the rest of its prompt plus the rest of its output). A replica's work is
    the sum over self.outstanding_requests(replica_id): the requests sent
    there that are still waiting or running.
    """

    def schedule(self) -> List[Tuple[int, Request]]:
        """Assign every request in self._request_queue (oldest first) to a
        replica. Return a list of (replica_id, request) pairs.

        For each request, pick the replica with the least outstanding work;
        on a tie, the lowest replica_id. Then add the request's work to that
        replica right away, so later requests in the same call see it.
        Keep these counts in local variables; do not call
        self.record_assignment, which the simulator calls for every pair
        you return.
        """
        self.sort_requests()
        request_mapping = []
        # [Part 5] TODO: sum each replica's outstanding work, then assign
        # every request in self._request_queue (pop from the front).
        # Replica ids: self._replica_schedulers.keys().
        loads = []
        for replica_id in self._replica_schedulers:
            tokens = sum(
                r.total_tokens - r.num_processed_tokens
                for r in self.outstanding_requests(replica_id)
            )
            loads.append([tokens, replica_id])
        loads.sort()

        while self._request_queue:
            request = self._request_queue.pop(0)
            request_mapping.append((loads[0][1], request))

            loads[0][0] += request.total_tokens - request.num_processed_tokens
            i = 0
            while i + 1 < len(loads) and loads[i + 1] < loads[i]:
                loads[i], loads[i + 1] = loads[i + 1], loads[i]
                i += 1
        # END OF YOUR CODE
        return request_mapping
