import math


def segment_confidence(seg):
    return math.exp(seg.avg_logprob) * (1 - seg.no_speech_prob)
