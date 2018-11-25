'''
Executes Salt highstate in Docker container
'''
from __future__ import print_function, unicode_literals
import os
import sys
import re
import random
import pprint
import numbers
import collections

import salt.client
import salt.config
import salt.loader


def is_windows():
    if sys.platform.startswith('win'):
        return True
    return False


def flatten_dict(d):
    def expand(key, value):
        if isinstance(value, dict):
            return [(k, v) for k, v in flatten_dict(value).items()]
        else:
            return [(key, value)]
    items = [item for k, v in d.items() for item in expand(k, v)]
    return dict(items)


def staterun_info(d, color=False):
    for k, v in d.items():
        dict_key = k.split('_|-')
        mod_name = '.'.join(dict_key[::len(dict_key)-1])
        highstate[mod_name] = highstate.pop(k)
        if isinstance(v, dict):
            result = [
                ('result', highstate[mod_name]['result']),
                ('name', highstate[mod_name]['name']),
                ('duration', highstate[mod_name]['duration']),
                ('start_time', highstate[mod_name]['start_time']),
                ('comment', highstate[mod_name]['comment'])
            ]
            if d[mod_name]['result']:
                if not is_windows() and color:
                    result.append(('test', '\033[32mPASS\033[0m'))
                else:
                    result.append(('test', 'PASS'))
            else:
                if not is_windows() and color:
                    result.append(('test', '\033[31mFAIL\033[0m'))
                else:
                    result.append(('test', 'FAIL'))
        yield {mod_name: result}


def output_staterun(state_output, color=False):
    info = []
    for output in staterun_info(state_output, color=color):
        for module, results in output.items():
            info.append('Test: {0}'.format(module))
            state_results = dict(results)
            state_pad = max(len(name) for name in state_results)
            for data in sorted(state_results, key=lambda x: x.lower()):
                value = str(state_results[data])
                value_pad = max(len(name) for name in str(state_results[data]))
                padding = max(state_pad, value_pad)
                if not is_windows() and color:
                    if 'pass' in value.lower():
                        col_code = '\033[1;32m'
                    elif 'fail' in value.lower():
                        col_code = '\033[1;31m'
                    else:
                        col_code = '\033[0m'
                    fmt = '{col}{0:>{pad}}: {1}\033[0m'.format(data,
                                                               value,
                                                               col=col_code,
                                                               pad=padding)
                else:
                    fmt = '{0:>{pad}}: {1}'
                run = fmt.format(data,
                                 value,
                                 pad=padding)
                info.append(run)
        info.append('\n')
    for line in info:
        yield line


if __name__ == '__main__':
    try:
        __opts__ = salt.config.minion_config('/etc/salt/minion')
        __grains__ = salt.loader.grains(__opts__)
        __opts__['grains'] = __grains__
        __utils__ = salt.loader.utils(__opts__)
        __salt__ = salt.loader.minion_mods(__opts__, utils=__utils__)
        highstate = __salt__['state.highstate']()
    except Exception:
        caller = salt.client.Caller()
        highstate = caller.function('state.highstate')

    root_dir = os.path.abspath(os.sep)
    results_dir = os.path.join(root_dir, 'srv', 'tests')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    results_file = os.path.join(results_dir, 'results.out')
    with open(results_file, 'w+') as fh:
        for output in output_staterun(highstate, color=True):
            print('{0}'.format(output))
