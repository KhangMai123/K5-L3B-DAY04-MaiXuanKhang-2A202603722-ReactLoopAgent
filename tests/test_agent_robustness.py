"""Additional behavioral regression tests; no network or credentials."""
import json
import unittest
from test_lab import FakeProvider, final, tool_call
from agent import run_agent
from status_tools import StatusTools


class RobustnessTests(unittest.TestCase):
    def test_raised_tool_exception_is_returned_with_original_id(self):
        class BrokenTools(StatusTools):
            def execute(self, name, args):
                raise TimeoutError('private request data')
        provider = FakeProvider([tool_call('unique', 'get_status', '{"provider":"github"}'), final()])
        result = run_agent('check', provider, BrokenTools())
        self.assertEqual(result['status'], 'completed')
        message = provider.histories[1][-1]
        self.assertEqual(message['tool_call_id'], 'unique')
        self.assertEqual(json.loads(message['content'])['error'], 'TimeoutError')
        self.assertNotIn('private request data', json.dumps(result))

    def test_provider_failure_counts_attempt_without_logging_exception_text(self):
        class BrokenProvider:
            def complete(self, messages, schemas):
                raise RuntimeError('HTTP 429 private-token')
        result = run_agent('check', BrokenProvider(), StatusTools())
        self.assertEqual(result['status'], 'error')
        self.assertEqual(len(result['usage']), 1)
        self.assertEqual(result['trace'][-1]['http_status'], 429)
        self.assertNotIn('private-token', json.dumps(result))

    def test_one_invalid_call_does_not_drop_second_result(self):
        first = tool_call('bad', 'get_status', '[]')
        second = tool_call('good', 'get_status', '{"provider":"github"}')
        first['calls'] += second['calls']
        first['message']['tool_calls'] += second['message']['tool_calls']
        provider = FakeProvider([first, final()])
        result = run_agent('check', provider, StatusTools())
        self.assertEqual(result['status'], 'completed')
        messages = provider.histories[1][-2:]
        self.assertEqual([m['tool_call_id'] for m in messages], ['bad', 'good'])
        self.assertEqual(json.loads(messages[0]['content'])['error'], 'INVALID_ARGUMENTS')
        self.assertEqual(json.loads(messages[1]['content'])['provider'], 'github')

    def test_unexpected_finish_and_empty_final_do_not_complete(self):
        for finish, text in [('content_filter', 'partial'), ('stop', '')]:
            reply = final(text)
            reply['finish'] = finish
            with self.subTest(finish=finish):
                self.assertEqual(run_agent('check', FakeProvider([reply]), StatusTools())['status'], 'error')


if __name__ == '__main__':
    unittest.main()
