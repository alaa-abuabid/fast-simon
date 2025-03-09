from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task(1)
    def ping1(self):
        self.client.get("/ping")

    @task(1)
    def ping2(self):
        self.client.get("/ping")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

if __name__ == "__main__":
    import os
    os.system("locust -f load_test.py --host=https://task3-dot-charged-state-451616-h7.ew.r.appspot.com")