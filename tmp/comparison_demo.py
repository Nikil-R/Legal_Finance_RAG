
import sys
import io
import asyncio
import os
import time
from dotenv import load_dotenv

# Force UTF-8 for terminal output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from app.generation.pipeline import RAGPipeline
from app.generation.llm_fabric import LLMFabric

# Load environment
load_dotenv()

async def run_comparison(question: str):
    print(f"\n[RUNNING SIDE-BY-SIDE COMPARISON]")
    print(f"QUESTION: {question}")
    print("-" * 60)
    
    pipeline = RAGPipeline()
    fabric = pipeline.generator.llm_fabric
    
    async def get_response(provider: str):
        # Swap primary provider for this call
        original = fabric.primary_provider
        fabric.primary_provider = provider
        
        start = time.perf_counter()
        try:
            res = await asyncio.to_thread(
                pipeline.run, 
                question=question, 
                domain="tax",
                session_id=None,
                owner_id="demo_user"
            )
            duration = (time.perf_counter() - start)
            return {
                "provider": provider,
                "answer": res.get("answer", "No answer found"),
                "duration": duration,
                "model": res.get("metadata", {}).get("model", "unknown"),
                "success": res.get("success", False),
                "error": res.get("error")
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"provider": provider, "error": str(e), "success": False}
        finally:
            fabric.primary_provider = original

    # Run Groq and Gemini concurrently
    print("QUERYING Groq (Llama) and Gemini 1.5 Pro...")
    tasks = [get_response("groq"), get_response("google")]
    results = await asyncio.gather(*tasks)
    
    for res in results:
        p_name = res["provider"].upper()
        if not res.get("success"):
            print(f"\n[ {p_name} ERROR ]: {res.get('error', 'Unknown')}")
            continue
            
        print(f"\n--- {p_name} VERSION --- {res['model']}")
        print(f"Latency: {res['duration']:.2f}s")
        print("-" * 30)
        # Indent answer for readability
        wrapped_answer = "\n".join(["   " + line for line in res['answer'].split("\n")][:10])
        print(wrapped_answer)
        if len(res['answer'].split("\n")) > 10:
            print("   ...")
    
    print("\n" + "=" * 60)
    print("COMPARISON COMPLETE")

if __name__ == "__main__":
    q = "What is the tax rate on income of 15 lakhs under the new regime for FY 2026-27?"
    asyncio.run(run_comparison(q))
