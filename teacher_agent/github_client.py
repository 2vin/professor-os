import base64
import hashlib
import json

from .config import settings
from .http_utils import request_with_retry


class GitHubPublisher(object):
    def __init__(self):
        if not settings.github_token or not settings.github_owner or not settings.github_repo:
            raise RuntimeError('GitHub publishing is enabled but GITHUB_TOKEN/GITHUB_OWNER/GITHUB_REPO is incomplete.')
        self.base = 'https://api.github.com/repos/{0}/{1}/contents'.format(
            settings.github_owner, settings.github_repo)
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': 'Bearer ' + settings.github_token,
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def put_bytes(self, path, content, message):
        url = self.base + '/' + path
        existing = request_with_retry(
            'GET', url,
            headers=self.headers,
            params={'ref': settings.github_branch},
            timeout=30,
            max_attempts=settings.api_max_attempts,
            base_delay=settings.api_retry_base_delay,
        )
        if existing.status_code not in (200, 404):
            existing.raise_for_status()

        payload = {
            'message': message,
            'content': base64.b64encode(content).decode('ascii'),
            'branch': settings.github_branch,
        }
        if existing.status_code == 200:
            payload['sha'] = existing.json()['sha']

        response = request_with_retry(
            'PUT', url,
            headers=self.headers,
            json=payload,
            timeout=45,
            max_attempts=settings.api_max_attempts,
            base_delay=settings.api_retry_base_delay,
        )
        response.raise_for_status()
        return response.json()

    def put_text(self, path, text, message):
        return self.put_bytes(path, text.encode('utf-8'), message)


class GitHubSourceSync(object):
    """Atomically sync validated project source files using GitHub's Git Data API."""
    def __init__(self):
        if not settings.github_token or not settings.github_owner or not settings.github_repo:
            raise RuntimeError('GITHUB_TOKEN/GITHUB_OWNER/GITHUB_REPO is incomplete.')
        self.repo_base = 'https://api.github.com/repos/{0}/{1}'.format(
            settings.github_owner, settings.github_repo)
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': 'Bearer ' + settings.github_token,
            'X-GitHub-Api-Version': '2022-11-28',
        }

    def _request(self, method, path, **kwargs):
        response = request_with_retry(
            method, self.repo_base + path,
            headers=self.headers,
            timeout=45,
            max_attempts=settings.api_max_attempts,
            base_delay=settings.api_retry_base_delay,
            **kwargs
        )
        return response

    def _bootstrap_if_empty(self):
        ref = self._request('GET', '/git/ref/heads/' + settings.github_branch)
        if ref.status_code == 200:
            return ref.json()['object']['sha']
        if ref.status_code != 404:
            ref.raise_for_status()
        payload = {
            'message': 'Initialize Professor OS repository',
            'content': base64.b64encode(b'# Professor OS\n').decode('ascii'),
        }
        create = self._request('PUT', '/contents/README.md', json=payload)
        if create.status_code not in (200, 201):
            create.raise_for_status()
        return create.json()['commit']['sha']

    def _remote_manifest_hash(self):
        response = self._request(
            'GET', '/contents/.professor_os_sync.json',
            params={'ref': settings.github_branch})
        if response.status_code == 404:
            return None
        response.raise_for_status()
        try:
            raw = base64.b64decode(response.json()['content']).decode('utf-8')
            return json.loads(raw).get('source_hash')
        except Exception:
            return None

    def sync_files(self, file_map, source_hash):
        if self._remote_manifest_hash() == source_hash:
            return {'changed': False, 'commit_sha': None}

        parent_sha = self._bootstrap_if_empty()
        commit = self._request('GET', '/git/commits/' + parent_sha)
        commit.raise_for_status()
        base_tree = commit.json()['tree']['sha']

        tree = []
        for path in sorted(file_map):
            content = file_map[path]
            blob = self._request('POST', '/git/blobs', json={
                'content': base64.b64encode(content).decode('ascii'),
                'encoding': 'base64',
            })
            blob.raise_for_status()
            tree.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob.json()['sha']})

        manifest = json.dumps({'source_hash': source_hash}, indent=2).encode('utf-8')
        blob = self._request('POST', '/git/blobs', json={
            'content': base64.b64encode(manifest).decode('ascii'), 'encoding': 'base64'})
        blob.raise_for_status()
        tree.append({'path': '.professor_os_sync.json', 'mode': '100644', 'type': 'blob', 'sha': blob.json()['sha']})

        new_tree = self._request('POST', '/git/trees', json={'base_tree': base_tree, 'tree': tree})
        new_tree.raise_for_status()
        new_commit = self._request('POST', '/git/commits', json={
            'message': 'Professor OS: validated automatic source sync',
            'tree': new_tree.json()['sha'],
            'parents': [parent_sha],
        })
        new_commit.raise_for_status()
        commit_sha = new_commit.json()['sha']
        update = self._request('PATCH', '/git/refs/heads/' + settings.github_branch,
                               json={'sha': commit_sha, 'force': False})
        update.raise_for_status()
        return {'changed': True, 'commit_sha': commit_sha}
