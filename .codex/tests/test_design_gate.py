from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "script"))


def test_spring_boot_contract_sets_domain_first_package_layout():
    import codex_work_items
    rows = codex_work_items.plan(
        "spring boot와 react로 커뮤니티 만들어줘",
        agents="backend,frontend",
    )
    contract = next(x for x in rows if x["key"] == "contract")
    backend = next(x for x in rows if x["key"] == "impl:post:backend")

    layout = contract["package_layout_contract"]
    assert any("domain-first modules" in x for x in layout)
    assert any("api, application, domain, infrastructure" in x for x in layout)
    assert any("shared owns response/exception" in x for x in layout)
    assert any("platform owns config/security/filter" in x for x in layout)
    assert any("top-level controller/service/repository" in x for x in layout)
    assert backend["package_layout_contract"] == layout


def test_package_layout_contract_is_spring_boot_specific():
    import codex_work_items
    rows = codex_work_items.plan(
        "fastapi react 커뮤니티 만들어줘",
        agents="backend,frontend",
    )
    contract = next(x for x in rows if x["key"] == "contract")
    backend = next(x for x in rows if x["agent"] == "backend")
    assert contract["package_layout_contract"] == []
    assert backend.get("package_layout_contract", []) == []


def test_nextjs_contract_uses_app_router_layout_without_vite_assumption():
    import codex_work_items
    rows = codex_work_items.plan(
        "nextjs mui axios zustand tanstack query 커뮤니티 만들어줘",
        agents="frontend",
    )
    contract = next(x for x in rows if x["key"] == "contract")
    frontend = next(x for x in rows if x["agent"] == "frontend")

    explicit = set(contract["framework_gate"]["explicit"])
    confirms = " ".join(contract["framework_gate"]["confirm"])
    layout = contract["frontend_layout_contract"]
    assert "Next.js" in explicit
    assert "rendering: Vite SPA or SSR/Next.js" not in confirms
    assert any("src/app App Router" in x for x in layout)
    assert any("page.tsx" in x for x in layout)
    assert any("use client" in x for x in layout)
    assert any("cache/revalidate/dynamic" in x for x in layout)
    assert frontend["frontend_layout_contract"] == layout
    assert any("framework=nextjs" in x for x in frontend["frontend_contract"])


def test_react_without_nextjs_keeps_rendering_choice_open():
    import codex_work_items
    rows = codex_work_items.plan("react mui 커뮤니티 만들어줘", agents="frontend")
    contract = next(x for x in rows if x["key"] == "contract")
    frontend = next(x for x in rows if x["agent"] == "frontend")
    assert any("Vite SPA or SSR/Next.js" in x for x in contract["framework_gate"]["confirm"])
    assert contract["frontend_layout_contract"] == []
    assert frontend.get("frontend_layout_contract", []) == []
