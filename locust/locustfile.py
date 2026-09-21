from locust import HttpUser, task, between
import random
import time
import string

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

class SampleAppUser(HttpUser):
    wait_time = between(5, 15)
    token = None

    def headers(self, auth=False):
        h = {
            'Content-Type': 'application/json',
            'Origin': 'http://host.docker.internal:3000'
        }
        if auth and self.token:
            h['Authorization'] = self.token
        return h

    def on_start(self):
        time.sleep(random.uniform(0, 3))
        self.email = f"{random_string()}@test.com"
        self.password = random_string(12)
        self.name = random_string(6)

        self.client.post('/api/register', json={
            'email': self.email,
            'password': self.password,
            'name': self.name
        }, headers=self.headers())

        response = self.client.post('/api/login', json={
            'email': self.email,
            'password': self.password
        }, headers=self.headers())

        if response.status_code == 200:
            self.token = response.json().get('token')

    @task(3)
    def check_session(self):
        self.client.get('/api/session', headers=self.headers(auth=True))

    @task(1)
    def logout_and_login(self):
        self.client.get('/api/logout', headers=self.headers(auth=True))
        response = self.client.post('/api/login', json={
            'email': self.email,
            'password': self.password
        }, headers=self.headers())
        if response.status_code == 200:
            self.token = response.json().get('token')

    @task(1)
    def failed_login(self):
        self.client.post('/api/login', json={
            'email': self.email,
            'password': random_string(12)
        }, headers=self.headers(), name='/api/login [failed]')