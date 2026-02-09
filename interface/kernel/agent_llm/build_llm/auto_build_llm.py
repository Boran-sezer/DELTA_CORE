import streamlit as st
from groq import Groq
from CONFIG import *

class DELTA_Agent:
    def __init__(self):
        # Remplacez 'VOTRE_CLE_API_ICI' par la clé obtenue sur Groq
        self.client = Groq(api_key="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")
        self.model = "llama-3.3-70b-versatile" # Modèle surpuissant et ultra-rapide

    def chat(self, prompt):
        """Envoie le message à Groq Cloud et retourne la réponse instantanément."""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Monsieur Sezer, une erreur de connexion au Cloud est survenue : {str(e)}"