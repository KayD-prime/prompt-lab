"""The practice model server: a pretend model API on your own computer, so the suite can run for free, offline,
and the same way every time (in CI, and whenever there is no key).

    python practice/practice_models.py [port]       default port 8100

It speaks the Chat Completions API (POST /v1/chat/completions, GET /v1/models), so the openai library talks to it
unchanged. It is not a model. Its triage answers come from a small table of the ten emails in inputs/emails.csv,
and it reacts to the PROMPT the way a real model tends to, so the course's story holds without a key:

    - a category the prompt does not name is never returned (the email falls to "Other");
    - "one sentence" in the prompt gives a one-sentence summary; otherwise two sentences;
    - sarcasm is read correctly only if the prompt mentions tone or sarcasm; otherwise the complaint is taken as praise
      (the real model did exactly this on email 6, in both captured runs);
    - praise (email 5) flips between "Other" and "Product" from one call to the next unless the prompt says what
      "Other" covers (the real model flipped email 5 between its two runs);
    - the wholesale enquiry (email 9) is "Product" unless the prompt says sales enquiries are "Other" (the real model
      said Product in both runs);
    - a quoted earlier thread is read as the request only if the prompt does not say to use the latest message; the
      practice server follows the latest message unless the prompt says "whole thread";
    - the "Category: / Summary:" lines appear only if the prompt asks for that format; otherwise prose;
    - a prompt that asks for urgency ("Urgency:") gets a Low / Medium / High line from the same table.

Any other question gets a fixed one-line reply. Real models vary between runs; this server does not, which is the point
of a check. The real model is for the lessons and the labs' "then for real" steps."""
import json
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8100
CATEGORIES = ["Billing", "Delivery", "Product", "Account", "Other"]

# (words that identify the email, true category, one-sentence summary, second sentence, quirk, urgency)
EMAILS = [
    (("charged twice", "4471"), "Billing", "The customer was charged twice for order #4471 and wants one payment refunded.", "They placed the order on 3 October.", None, "High"),
    (("nothing has arrived", "4502"), "Delivery", "Order #4502 shows as delivered but has not arrived, so the customer wants it traced or replaced.", "They have already checked with their neighbours.", None, "High"),
    (("chipped",), "Product", "A mug arrived chipped and the customer is still waiting for the refund promised for a broken teapot.", "The teapot refund was promised two weeks ago.", None, "Medium"),
    (("where is it",), "Delivery", "The customer is asking where their order is.", "No order number or details were given.", "no-context", "Medium"),
    (("autumn range", "candle"), "Other", "The customer is praising the new autumn range and needs nothing.", "They particularly liked the candle.", "flip", "Low"),
    (("tracking link",), "Delivery", "The tracking link has failed for the third time this month and the customer is frustrated.", "The message is sarcastic.", "sarcasm", "High"),
    (("mot de passe", "connecter"), "Account", "The customer cannot log in since yesterday because their password is refused.", "The email is in French.", "french", "Medium"),
    (("change the email address",), "Account", "The customer wants to change the email address on their account.", "They also thanked support for sorting an earlier late delivery.", "quoted", "Low"),
    (("wholesale", "200"), "Other", "A café owner is asking about wholesale pricing for about 200 speckled mugs for a November opening.", "This is a sales enquiry rather than a support problem.", "sales", "Low"),
    (("account is locked", "reset email"), "Account", "The customer's account is locked and the password reset email never arrives.", "Their previous order arrived on time and they have been a customer for years.", None, "High"),
]


CALLS = {}      # how often each email has been asked about: used to make the "flip" emails change between runs


def triage(prompt: str, email: str):
    """The canned triage answer for one email, shaped by what the prompt asks for."""
    low = prompt.lower(); e = email.lower()
    named = [c for c in CATEGORIES if c.lower() in low]
    for words, cat, one, two, quirk, urgency in EMAILS:
        if all(w in e for w in words):
            break
    else:
        return None
    CALLS[words] = CALLS.get(words, 0) + 1
    if quirk == "sarcasm" and not re.search(r"sarcas|tone|frustrat|complain", low):
        one = "The customer is pleased that the tracking link is working well and is happy with the delivery experience."
    if quirk == "flip" and not re.search(r"praise|feedback|not a problem", low) and CALLS[words] % 2 == 0:
        cat = "Product"
    if quirk == "sales" and not re.search(r"sales|wholesale|enquir|inquir", low):
        cat = "Product"
    if quirk == "french" and re.search(r"same language|customer's language|in french", low):
        one = "Le client ne peut plus se connecter depuis hier car son mot de passe est refusé."
    if quirk == "quoted" and re.search(r"whole thread|entire thread|everything in the email", low):
        cat, one = "Delivery", "The customer's late order has been replaced and they are thanking support; they also want their email address changed."
    if cat not in named:
        cat = "Other" if "other" in [n.lower() for n in named] or not named else named[-1]
    summary = one if re.search(r"one[- ]sentence|a single sentence|in one line", low) else f"{one} {two}"
    if "urgency:" in low:
        return f"Urgency: {urgency}\nReason: {one}"
    if "category:" in low and "summary:" in low:
        return f"Category: {cat}\nSummary: {summary}"
    return f"This email is about {cat.lower()}. {summary}"


def reply(messages):
    prompt = "\n".join(m.get("content", "") for m in messages if m.get("role") != "assistant")
    email = messages[-1].get("content", "")
    m = re.search(r"email:\s*(.*?)(?:\n\s*reply in this format.*)?$", email, re.I | re.S)
    if m:
        email = m.group(1)
    prompt = prompt.replace(email, "")           # judge the instructions, not the customer's own words
    ans = triage(prompt, email)
    if ans is None:
        short = email.strip().replace("\n", " ")[:60]
        ans = f"Practice reply to “{short}”. The practice server always answers this way, so a check can run without spending anything."
    return ans


def tokens(text):
    return max(1, len(text) // 4)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def send(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        if self.path.rstrip("/").endswith("/models"):
            return self.send(200, {"object": "list", "data": [{"id": "practice-model", "object": "model", "owned_by": "promptlab"}]})
        self.send(404, {"error": {"message": f"no such path {self.path}", "type": "invalid_request_error"}})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0); body = json.loads(self.rfile.read(n) or b"{}")
        if not self.path.rstrip("/").endswith("/chat/completions"):
            return self.send(404, {"error": {"message": f"no such path {self.path}", "type": "invalid_request_error"}})
        msgs = body.get("messages", []); text = reply(msgs)
        pin = sum(tokens(m.get("content", "")) for m in msgs)
        self.send(200, {"id": "chatcmpl-practice", "object": "chat.completion", "created": int(time.time()), "model": body.get("model", "practice-model"),
                        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": pin, "completion_tokens": tokens(text), "total_tokens": pin + tokens(text)}})


if __name__ == "__main__":
    print(f"practice model server on http://127.0.0.1:{PORT}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
