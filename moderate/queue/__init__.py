import logging 
__all__ = ['queue']

_adapters = dict()

logger = logging.getLogger('moderate.queue')

def queue(adapter, **options):
    backed = _adapters.get(adapter)
    prefix = adapter.capitalize()
    if not backed:
        try:
            backed = __import__('moderate.queue.' + adapter + '_queue', globals(), locals(), [prefix + 'Queue'])
            backed = getattr(backed, prefix + 'Queue')
        except ImportError:
            logger.error('Can\'t find the adapter : %s', adapter)
            exit(1)
        _adapters[adapter] = backed 
    return backed(**options)