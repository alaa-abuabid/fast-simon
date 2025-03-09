from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    @task(1)
    def query_dress(self):
        self.client.get("/related?query=dress")

    @task(1)
    def query_shoes(self):
        self.client.get("/related?query=shoes")

    @task(1)
    def query_nonexistent(self):
        self.client.get("/related?query=balck mini dresses")

    @task(1)
    def query_unique(self):
        self.client.get("/related?query=uniquequery")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

if __name__ == "__main__":
    import os
    os.system("locust -f load_test.py --host=https://task3-dot-charged-state-451616-h7.ew.r.appspot.com")