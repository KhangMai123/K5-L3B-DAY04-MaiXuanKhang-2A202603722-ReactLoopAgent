"""Compatible endpoint configuration without making network requests."""
import os
import unittest
from unittest.mock import patch
from providers import Provider, CONFIG


class EndpointTests(unittest.TestCase):
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'dummy',
                            'OPENAI_BASE_URL': 'https://api.deepseek.com/'})
    @patch('providers.post_json')
    def test_direct_deepseek_endpoint_and_authorization(self, post):
        post.return_value = {'choices': [{'message': {'role': 'assistant', 'content': 'ok'},
                                         'finish_reason': 'stop'}]}
        client = Provider('openai', 'test-model')
        for _ in range(2):
            client.complete([{'role': 'user', 'content': 'check'}], [])
        requests = post.call_args_list
        self.assertEqual(requests[0].args[0], 'https://api.deepseek.com/chat/completions')
        self.assertEqual(requests[0].args[1]['Authorization'], 'Bearer dummy')
        self.assertNotIn('x-opencode-session', requests[0].args[1])
        self.assertNotIn('dummy', str(requests[0].args[2]))

    @patch.dict(os.environ, {'GEMINI_API_KEY': 'dummy', 'OPENAI_BASE_URL': 'https://example.invalid'})
    def test_gemini_adapter_is_not_redirected(self):
        self.assertEqual(Provider('gemini', 'test-model').url, CONFIG['gemini'][1])


if __name__ == '__main__':
    unittest.main()
