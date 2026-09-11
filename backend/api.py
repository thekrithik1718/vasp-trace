from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from backend.graph.data_loader import load_and_validate_transactions
from backend.graph.graph_builder import build_transaction_graph
from backend.graph.traversal import traverse_transactions
from backend.scoring.schemas import GraphInput
from backend.scoring.vasp_detector import VaspDetector
from backend.scoring.pipeline import run_scoring_pipeline

app = FastAPI(title="VASP Trace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TraceRequest(BaseModel):
    address: str
    hop_depth: int

CSV_PATH = os.path.join(os.path.dirname(__file__), "graph", "sample_data.csv")
KNOWN_VASPS_PATH = os.path.join(os.path.dirname(__file__), "scoring", "data", "known_vasps.csv")

_graph = None
_vasp_detector = None

def get_graph():
    global _graph
    if _graph is None:
        try:
            df = load_and_validate_transactions(CSV_PATH)
            _graph = build_transaction_graph(df)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize transaction graph: {str(e)}")
    return _graph

def get_vasp_detector():
    global _vasp_detector
    if _vasp_detector is None:
        try:
            _vasp_detector = VaspDetector(KNOWN_VASPS_PATH)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize VaspDetector: {str(e)}")
    return _vasp_detector

@app.post("/api/trace")
def trace_wallet(req: TraceRequest):
    try:
        graph = get_graph()
    except Exception:
        raise HTTPException(status_code=500, detail="Missing dataset or internal graph error")

    try:
        vasp_detector = get_vasp_detector()
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected backend error")

    if req.address not in graph:
        raise HTTPException(status_code=400, detail="Source wallet not found")

    if req.hop_depth < 1:
        raise HTTPException(status_code=400, detail="Invalid request")

    try:
        traversal_result = traverse_transactions(graph, req.address, req.hop_depth)
        graph_input = GraphInput(**traversal_result)
        scoring_results = run_scoring_pipeline(graph_input, vasp_detector)

        return {
            "source_wallet": graph_input.source_wallet,
            "paths": [path.model_dump(by_alias=True) for path in graph_input.paths],
            "scoring_results": [res.model_dump() for res in scoring_results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected backend error")
