(ns core.ai-gateway.ollama-provider
  "Clojure counterpart of core.ai_gateway.ollama_gateway.OllamaGateway.

   Thin wrapper around Ollama's /api/chat endpoint using clj-http, mirroring
   what the Python side does through Strands' OllamaModel: one function for
   free-form text generation, one for JSON-schema-constrained structured
   output (Ollama's `:format` parameter, same mechanism used in the
   ollama-structured.clj example)."
  (:require [clj-http.client :as http]
            [cheshire.core :as json]))

(defn- chat-url [host]
  (str host "/api/chat"))

(defn- build-messages [system-prompt prompt]
  (cond-> []
    (some? system-prompt) (conj {:role "system" :content system-prompt})
    true (conj {:role "user" :content prompt})))

(defn- post-chat [host payload]
  (:body (http/post (chat-url host)
                     {:body         (json/generate-string payload)
                      :content-type :json
                      :accept       :json
                      :as           :json})))

(defn generate-text
  "Sends `prompt` (with an optional `system-prompt`) to the Ollama server at
   `host` for `model`, and returns the raw text of the model's reply.

   opts: {:host :model :system-prompt (optional) :prompt}"
  [{:keys [host model system-prompt prompt]}]
  (let [payload {:model    model
                 :messages (build-messages system-prompt prompt)
                 :stream   false}
        body    (post-chat host payload)]
    (get-in body [:message :content])))

(defn generate-structured
  "Same as `generate-text`, but constrains the reply to `schema` (a JSON
   Schema map) via Ollama's structured-output `:format` parameter, and
   parses the reply back into a Clojure map (string keys, so it round-trips
   cleanly through cheshire/generate-string on the way back out).

   opts: {:host :model :system-prompt (optional) :prompt :schema}

   Returns nil if the model returned no content."
  [{:keys [host model system-prompt prompt schema]}]
  (let [payload {:model    model
                 :messages (build-messages system-prompt prompt)
                 :stream   false
                 :format   schema}
        body    (post-chat host payload)
        content (get-in body [:message :content])]
    (when content
      (json/parse-string content))))