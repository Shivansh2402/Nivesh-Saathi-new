from metahackathonfinance import app
import uvicorn


if __name__ == "__main__":
    uvicorn.run("metahackathonfinance:app", port=8002)