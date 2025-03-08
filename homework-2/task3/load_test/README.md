# Load Testing with Locust

## Overview

This project contains a load testing script for the `related` API endpoint of a Google App Engine application. The load test is designed to simulate user behavior and measure the performance of the API under concurrent requests. By using Locust, we can ensure that the application can handle multiple users simultaneously and identify any potential performance bottlenecks.

## Load Test Workflow

1. **User Behavior**:
   - The load test simulates user interactions with the `related` API endpoint by sending GET requests with different query parameters.

2. **Tasks**:
   - The script defines tasks for querying different types of search terms (e.g., "dress", "shoes", "nonexistentquery", "uniquequery").

3. **Execution**:
   - The script uses Locust to simulate multiple users performing these tasks concurrently, measuring response times, error rates, and throughput.

4. **Running the Load Test**:
   - Run the load test script:
     ```bash
     python load_test.py
     ```
   - Open the Locust web interface by going to `http://localhost:8089` in a web browser.
   - Configure the number of users and spawn rate, then start the test.

## Conclusion

This load test helps ensure that the `related` API endpoint can handle concurrent requests efficiently and performs well under load. By simulating user behavior, you can identify potential performance bottlenecks and optimize your application accordingly. If you have any questions or need further assistance, feel free to reach out!

---

Feel free to customize this README file further to fit your specific project requirements. If you need any more help, just let me know!