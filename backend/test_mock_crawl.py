import asyncio
from backend.agent.flow_crawler import AutonomousFlowCrawler

async def test_crawler_mock():
    crawler = AutonomousFlowCrawler()
    
    print("=== TEST 1: GymTrap Cancellation Flow ===")
    res_gym = await crawler.run_scan(
        target_url="http://127.0.0.1:8000/mock/gymtrap",
        flow_type="cancellation",
        max_steps=4
    )
    print(f"GymTrap Total Nodes Traversed: {res_gym['total_steps']}")
    print(f"GymTrap Manipulation Score: {res_gym['score_summary']['manipulation_index']}/100")
    for step in res_gym["steps"]:
        print(f"  - Step {step['step_number']}: {step['title']} | CTAs: {len(step['buttons'])} | Findings: {step['findings_count']}")

    print("\n=== TEST 2: ShopSneak Checkout Flow ===")
    res_shop = await crawler.run_scan(
        target_url="http://127.0.0.1:8000/mock/shopsneak",
        flow_type="checkout",
        max_steps=4
    )
    print(f"ShopSneak Total Nodes Traversed: {res_shop['total_steps']}")
    print(f"ShopSneak Manipulation Score: {res_shop['score_summary']['manipulation_index']}/100")
    for step in res_shop["steps"]:
        print(f"  - Step {step['step_number']}: {step['title']} | CTAs: {len(step['buttons'])} | Findings: {step['findings_count']}")

if __name__ == "__main__":
    asyncio.run(test_crawler_mock())

