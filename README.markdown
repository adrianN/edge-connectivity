Edge-Connectivity
=================

This provides a prototype implementation of a certifying 3-edge-connectivity algorithm. The algorithm can be made linear, by replacing the sorting in `interval_ordering.py` by bucket-sort. But since sorting takes only a tiny part of the execution time, this is most likely wasted effort.