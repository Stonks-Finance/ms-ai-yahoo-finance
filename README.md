# AI Microservice for Stonks Finance
![](./readme_images/stonks-image.jpg)

`ms-ai-yahoo-finance` is the AI microservice for the **Stonks Finance** project. This service is responsible for fetching stock data from Yahoo Finance, training AI models, and providing predictions about stock performance. It exposes a RESTful API to interact with the trained models and get information about changes in stock values, allowing other microservices, such as `ms-main`, to access data insights and predictions.

## Features
- **Fetch Stock Data**: Integrates with Yahoo Finance to retrieve real-time and historical stock data.
- **Train AI Models**: Builds machine learning models for analyzing and predicting stock trends.
- **RESTFul API**: Offers endpoints for querying stock changes and forecasting future performance.
- **Python FastAPI Implementation**: Ensures a lightweight and efficient microservice.

## Architecture
The `ms-ai-yahoo-finance` microservice is part of the **Stonks Finance** architecture, interacting with:
- **ms-main**: API Gateway for request routing.
- **Frontend**: ReactJS-based UI that visualizes stock data and predictions.

## Getting Started

### Prerequisites
Ensure the following are installed:
- **Python 3.9** or later
- **Docker** 

### Clone the Repository
```bash
git clone https://github.com/Stonks-Finance/ms-ai-yahoo-finance.git
cd ms-ai-yahoo-finance
```

### Install Dependencies
If you will run the application locally, you should create a virtual environment and install the required Python packages:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
But if you will run the application using Docker, you can pass this part.

### Run the Application

#### Locally
```bash
python -m main.py
```

#### Using Docker
1. Build the Docker image:
   ```bash
   docker build -t stonks-ms-ai-yahoo-finance .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 --name stonks-ms-ai-yahoo-finance stonks-ms-ai-yahoo-finance
   ```

After running application, you can just go to `http://localhost:8000/docs` to meet the API Documentation of it. 

## CI/CD Part
This project includes CI/CD also. It is continuously deploying to the **Render**, using **Github Actions**. If you want to see URL of this microservice, you can just go to <a href="https://ms-main.onrender.com/">https://ms-main.onrender.com/</a>. 

But you should consider one thing, that this project uses Render freely. And because of that, the requests can delay 50 seconds or more. It is something about Render Policy. It says : 

<i>
Free instances spin down after periods of inactivity. They do not support SSH access, scaling, one-off jobs, or persistent disks. Select any paid instance type to enable these features.
</i>

## Contributing
Contributions are welcome! Follow these steps to contribute:
* Fork the project.
* Create a new branch: `git checkout -b feature/your-feature`. 
* Add your new features.
* Submit a pull request. 

## Thanks for your attention! 