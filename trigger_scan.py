import os
import anthropic

client = anthropic.Anthropic()

SESSION_ID = os.environ.get("SESSION_ID", "sesn_01E52Cj4Knd747JV6aGPojhp")
AGENT_ID = "agent_013AVwEUVjjpXr9hSp8LPKnC"
ENV_ID = "env_01AeV5qPrW3Vk9btjVnZsAbC"
VAULT_IDS = ["vlt_011CbGHRWtBdAqmTWUASZMWQ"]
MEMORY_STORE_ID = "memstore_01BQVQrATLVAKJH5ipCyXcC3"


def get_or_create_session():
    try:
        session = client.beta.sessions.retrieve(SESSION_ID)
        if session.status != "terminated":
            return session.id
    except Exception:
        pass

    session = client.beta.sessions.create(
        agent=AGENT_ID,
        environment_id=ENV_ID,
        vault_ids=VAULT_IDS,
        resources=[{
            "type": "memory_store",
            "memory_store_id": MEMORY_STORE_ID,
            "access": "read_write",
            "instructions": "Store list of interesting companies, as well as what news have been sent so no double info is sent out.",
        }],
    )
    # Print so you can update SESSION_ID if needed
    print(f"Created new session: {session.id}")
    return session.id


def send_and_wait(message: str) -> str:
    sid = get_or_create_session()

    client.beta.sessions.events.send(
        session_id=sid,
        events=[{"type": "user.message", "content": [{"type": "text", "text": message}]}],
    )

    response_parts = []
    for event in client.beta.sessions.events.stream(session_id=sid):
        if event.type == "agent.message":
            for block in event.content:
                if block.type == "text":
                    response_parts.append(block.text)
        if event.type == "session.status_idle" and getattr(event, "stop_reason", None) and event.stop_reason.type == "end_turn":
            break

    return "\n".join(response_parts)


if __name__ == "__main__":
    print(send_and_wait("Run a market scan now and post findings to Slack"))