"""Source gate and bounded rate limits, independent of eval answers/IDs."""
import json
import unittest
from unittest.mock import patch
from agent import run_agent
from bonus.tools import BonusTools
from status_tools import StatusTools
from test_lab import FakeProvider, final, tool_call


class GuardTests(unittest.TestCase):
    def test_persistent_429_caps_real_execution_even_when_model_asks_again(self):
        tools = BonusTools(scenario='rate_limit_always')
        responses = [tool_call(str(i), 'get_vercel_status', '{}') for i in range(4)] + [final('Unknown status')]
        provider = FakeProvider(responses)
        result = run_agent('check', provider, tools, max_steps=5)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(tools.calls[('get_vercel_status','vercel')], 3)
        self.assertFalse(json.loads(provider.histories[3][-1]['content'])['retry_allowed'])
        self.assertEqual(json.loads(provider.histories[4][-1]['content'])['error'], 'RETRY_EXHAUSTED')

    @patch('agent.time.sleep')
    def test_retry_after_is_respected(self, sleep):
        class Limited(StatusTools):
            def __init__(self): super().__init__(); self.count = 0
            def execute(self, name, args):
                self.count += 1
                if self.count == 1:
                    return {'ok':False,'error':'RATE_LIMITED','http_status':429,'retry_after':'2'}
                return super().execute(name,args)
        p = FakeProvider([tool_call('a','get_status','{"provider":"github"}'),
                          tool_call('b','get_status','{"provider":"github"}'),final()])
        result = run_agent('check',p,Limited())
        self.assertEqual(result['status'],'completed')
        sleep.assert_called_once_with(2.0)
        self.assertTrue(any(t['event']=='retry_wait' for t in result['trace']))

    @patch('agent.time.sleep')
    def test_long_retry_after_stops_instead_of_shortening_server_delay(self, sleep):
        class Limited(StatusTools):
            def execute(self, name, args):
                return {'ok':False,'http_status':429,'retry_after_seconds':120}
        p = FakeProvider([tool_call('a','get_status','{"provider":"github"}'),
                          tool_call('b','get_status','{"provider":"github"}'),final('Cannot verify')])
        result = run_agent('check',p,Limited())
        self.assertEqual(result['status'],'completed')
        sleep.assert_not_called()
        self.assertEqual(json.loads(p.histories[2][-1]['content'])['error'],'RETRY_EXHAUSTED')

    def test_empty_json_arguments_get_observation(self):
        p=FakeProvider([tool_call('a','get_status',''),final()])
        self.assertEqual(run_agent('check',p,StatusTools())['status'],'completed')
        self.assertEqual(json.loads(p.histories[1][-1]['content'])['error'],'INVALID_ARGUMENTS')

    def test_malformed_provider_result_is_error(self):
        result=run_agent('check',FakeProvider([None]),StatusTools())
        self.assertEqual(result['status'],'error')
        self.assertEqual(result['error'],'MALFORMED_MODEL_RESPONSE')

    def test_url_prefix_is_not_a_valid_source_match(self):
        class Details(StatusTools):
            def execute(self,name,args):
                return {'ok':True,'url':'https://status.example/incident/abc'}
        p=FakeProvider([tool_call('a','get_incident_details','{"provider":"github","incident_id":"demo"}'),
                        final('https://status.example/incident/abc-fabricated')])
        self.assertEqual(run_agent('check',p,Details(),max_steps=2)['status'],'max_steps')

    def test_gate_tracks_each_successful_incident(self):
        class Details(StatusTools):
            def execute(self,name,args):
                return {'ok':True,'url':'https://status.example/incident/'+args['incident_id']}
        first=tool_call('a','get_incident_details','{"provider":"github","incident_id":"one"}')
        second=tool_call('b','get_incident_details','{"provider":"github","incident_id":"two"}')
        first['calls']+=second['calls']; first['message']['tool_calls']+=second['message']['tool_calls']
        p=FakeProvider([first,final('https://status.example/incident/one'),
                        final('Sources: https://status.example/incident/one https://status.example/incident/two')])
        result=run_agent('check',p,Details(),max_steps=3)
        self.assertEqual(result['status'],'completed')
        self.assertEqual(len(result['usage']),3)
        self.assertEqual([t['event'] for t in result['trace']].count('validation_missing_source'),1)


if __name__=='__main__': unittest.main()
