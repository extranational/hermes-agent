from types import SimpleNamespace

from agent.turn_finalizer import finalize_turn


def _minimal_agent():
    agent = SimpleNamespace()
    agent.max_iterations = 90
    agent.iteration_budget = SimpleNamespace(remaining=10, used=1, max_total=90)
    agent.quiet_mode = True
    agent.model = "test-model"
    agent.provider = "test-provider"
    agent.base_url = "https://example.test/v1"
    agent.session_id = "session-1"
    agent.session_input_tokens = 0
    agent.session_output_tokens = 0
    agent.session_cache_read_tokens = 0
    agent.session_cache_write_tokens = 0
    agent.session_reasoning_tokens = 0
    agent.session_prompt_tokens = 0
    agent.session_completion_tokens = 0
    agent.session_total_tokens = 0
    agent.session_estimated_cost_usd = 0.0
    agent.session_cost_status = "unknown"
    agent.session_cost_source = "none"
    agent.context_compressor = SimpleNamespace(last_prompt_tokens=0)
    agent._turn_failed_file_mutations = {}
    agent._tool_guardrail_halt_decision = None
    agent._response_was_previewed = False
    agent._interrupt_message = None
    agent._stream_callback = object()
    agent._skill_nudge_interval = 0
    agent._iters_since_skill = 0
    agent.valid_tool_names = []

    agent._emit_status = lambda *_a, **_k: None
    agent._safe_print = lambda *_a, **_k: None
    agent._handle_max_iterations = lambda *_a, **_k: "summary"
    agent._save_trajectory = lambda *_a, **_k: None
    agent._cleanup_task_resources = lambda *_a, **_k: None
    agent._drop_trailing_empty_response_scaffolding = lambda *_a, **_k: None
    agent._persist_session = lambda *_a, **_k: None
    agent._file_mutation_verifier_enabled = lambda: False
    agent._format_file_mutation_failure_footer = lambda *_a, **_k: ""
    agent._turn_completion_explainer_enabled = lambda: False
    agent._format_turn_completion_explanation = lambda *_a, **_k: ""
    agent._drain_pending_steer = lambda: None
    agent.clear_interrupt = lambda: None
    agent._sync_external_memory_for_turn = lambda **_k: None
    agent._spawn_background_review = lambda **_k: None
    return agent


def test_post_llm_call_receives_same_turn_assistant_reasoning(monkeypatch):
    calls = []

    def fake_invoke_hook(name, **kwargs):
        calls.append((name, kwargs))
        return []

    monkeypatch.setattr("hermes_cli.plugins.invoke_hook", fake_invoke_hook)

    messages = [
        {"role": "user", "content": "previous"},
        {"role": "assistant", "content": "old", "reasoning": "old reasoning"},
        {"role": "user", "content": "current"},
        {"role": "assistant", "content": None, "reasoning": "same-turn reasoning"},
        {"role": "tool", "content": "tool result"},
        {"role": "assistant", "content": "done"},
    ]

    result = finalize_turn(
        _minimal_agent(),
        final_response="done",
        api_call_count=1,
        interrupted=False,
        failed=False,
        messages=messages,
        conversation_history=[],
        effective_task_id="task-1",
        turn_id="turn-1",
        user_message="current",
        original_user_message="current",
        _should_review_memory=False,
        _turn_exit_reason="text_response(4)",
    )

    post_calls = [kwargs for name, kwargs in calls if name == "post_llm_call"]
    assert post_calls
    assert post_calls[0]["assistant_reasoning"] == "same-turn reasoning"
    assert result["last_reasoning"] == "same-turn reasoning"
