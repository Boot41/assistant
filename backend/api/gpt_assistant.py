import logging
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Q, F, Value, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce, Greatest
from django.core.cache import cache
from typing import List
from .models import UniversalContent
from .ai_models import AIModelFactory
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTAssistant:
    """
    GPTAssistant is responsible for generating AI responses based on user input
    and the recent conversation context. It utilizes retrieval-augmented generation (RAG)
    to fetch relevant information from the database to provide accurate and contextually
    appropriate responses.
    """
    def __init__(self, model_name='4o-mini'):
        """
        Initializes the GPTAssistant with the specified AI model.

        Args:
            model_name (str): The name of the AI model to use.
        """
        self.model_name = model_name
        self.ai_model = AIModelFactory.get_model(model_name)
        self.full_response = ""
        self.engagement_phrases = [
            "What would you like to explore next?",
            "Is there a particular aspect you're curious about?",
            "How can I provide more detailed information for you?",
            "Which part of Think41 intrigues you the most?",
            "What other areas of our company would you like to discover?",
            "Is there anything specific you'd like me to elaborate on?",
            "Where shall we focus our exploration next?",
            "What other questions do you have about Think41?",
            "How else can I assist you in learning about our company?",
            "Which of our services or areas would you like to know more about?"
        ]

    def generate_response(self, user_input: str, context: str = '') -> dict:
        """
        Generates a response to the user's input by incorporating recent conversation context
        and relevant information fetched from the database.

        Args:
            user_input (str): The latest input from the user.
            context (str): The recent conversation context.

        Returns:
            dict: A dictionary containing the AI's response and a flag indicating if more information is available.
        """
        logger.info(f"Generating response for user input: {user_input}")
        
        # Retrieve additional context using RAG
        additional_context = self.get_context(user_input)
        full_context = f"{context}\n\n{additional_context}".strip()
        
        # Construct the prompt with recent conversation history and guidelines
        prompt = f"""You are an AI assistant for Think41, a technology consulting company with a product mindset. Your role is to provide knowledgeable and helpful information about the company. Always maintain a professional, friendly, and helpful tone.

Recent conversation history:
{full_context}

User's latest input: '{user_input}'

Guidelines:
1. Provide a concise response (50-75 words) that addresses the main point of the user's query.
2. Use the conversation history to maintain context and provide relevant responses.
3. If the user asks about Think41's services, founders, background, or any related information, focus on the most relevant details.
4. For unrelated questions, politely redirect to Think41 topics.
5. Address inappropriate language with a brief, polite message about professional communication.
6. If unsure, offer to help find information on the Think41 website or suggest contacting Think41 directly.
7. Always maintain a professional, friendly, and helpful tone.

Response:"""
        
        # Generate AI response using the AI model
        ai_response = self.ai_model.generate_response(prompt)
        
        if ai_response:
            ai_response = ai_response.strip()
            engagement_phrase = random.choice(self.engagement_phrases)
            response = f"{ai_response}\n\n{engagement_phrase}"
            self.full_response = ai_response
        else:
            response = "I apologize, but I'm having trouble generating a response at the moment. How else can I assist you with information about Think41?"
            self.full_response = ""
        
        logger.info(f"Generated response: {response[:100]}...")  # Log first 100 characters of the response

        return {
            "response": response,
            "has_more_info": bool(self.full_response)
        }

    def get_more_info(self) -> dict:
        """
        Provides additional information based on the last generated response.

        Returns:
            dict: A dictionary containing the additional information response.
        """
        if self.full_response:
            return {"response": self.full_response}
        else:
            return {
                "response": "I'm sorry, but I don't have any additional information on this topic at the moment. Is there anything else you'd like me to elaborate on regarding Think41 or navigating our website?"
            }

    def get_context(self, user_input: str) -> str:
        """
        Retrieves relevant content from the database based on the user's input using RAG.

        Args:
            user_input (str): The latest input from the user.

        Returns:
            str: A concatenated string of relevant content titles and contents.
        """
        relevant_content = self.search_relevant_content(user_input)
        context = ""
        
        if relevant_content:
            logger.info(f"Found {len(relevant_content)} relevant content items")
            for content in relevant_content:
                logger.info(f"Content item: Title: {content.title}, Type: {content.content_type}")
                context += f"{content.title}:\n{content.content}\n\n"
        else:
            logger.info("No relevant content found, using default context")
            context = "No specific context found in the database. Please provide a general response based on the user's input."

        return context

    def search_relevant_content(self, query: str) -> List[UniversalContent]:
        """
        Searches for relevant content in the database using full-text search and trigram similarity.
        Incorporates performance optimizations and error handling for production readiness.

        Args:
            query (str): The search query derived from the user's input.

        Returns:
            List[UniversalContent]: A list of top 5 relevant UniversalContent objects.
        """
        try:
            logger.info(f"Searching for relevant content with query: {query}")

            # Normalize the query
            normalized_query = query.lower().strip()

            # Check cache first
            cache_key = f"search_relevant_content:{normalized_query}"
            cached_results = cache.get(cache_key)
            if cached_results:
                logger.info("Returning cached search results")
                return cached_results

            # Create a full-text search query
            search_query = SearchQuery(normalized_query, config='english')

            # Annotate the queryset with relevance scores
            relevant_content = UniversalContent.objects.annotate(
                search_rank=Coalesce(SearchRank(F('search_vector'), search_query), Value(0.0)),
                title_rank=Coalesce(
                    SearchRank(
                        F('search_vector'),
                        SearchQuery(normalized_query, config='english', search_type='phrase')
                    ), Value(0.0)
                ),
                content_rank=Coalesce(SearchRank(F('search_vector'), search_query), Value(0.0)),
                trigram_similarity_title=TrigramSimilarity('title', normalized_query),
                trigram_similarity_content=TrigramSimilarity('content', normalized_query),
                combined_rank=ExpressionWrapper(
                    F('search_rank') * 2 +
                    F('title_rank') * 3 +
                    F('content_rank') * 1.5 +
                    Greatest(F('trigram_similarity_title') * 2, F('trigram_similarity_content')),
                    output_field=FloatField()
                )
            ).filter(
                Q(search_vector=search_query) |
                Q(title__icontains=normalized_query) |
                Q(content__icontains=normalized_query) |
                Q(trigram_similarity_title__gt=0.1) |
                Q(trigram_similarity_content__gt=0.1)
            ).order_by('-combined_rank').only('id', 'title', 'content')  # Select only necessary fields

            found_results = relevant_content.count()
            logger.info(f"Initial search found {found_results} results")

            # If no results or low-quality results, try word-by-word search
            if not relevant_content.exists() or relevant_content.first().combined_rank < 0.1:
                logger.info("No results or low-quality results found, trying word-by-word search")
                words = normalized_query.split()
                q_objects = Q()
                for word in words:
                    q_objects |= Q(title__icontains=word) | Q(content__icontains=word)
                
                word_query = ' '.join(words)
                word_search_query = SearchQuery(word_query, config='english')

                word_by_word_content = UniversalContent.objects.filter(q_objects).distinct().annotate(
                    search_rank=Coalesce(SearchRank(F('search_vector'), word_search_query), Value(0.0)),
                    title_rank=Coalesce(
                        SearchRank(
                            F('search_vector'),
                            SearchQuery(word_query, config='english', search_type='phrase')
                        ), Value(0.0)
                    ),
                    content_rank=Coalesce(SearchRank(F('search_vector'), word_search_query), Value(0.0)),
                )

                # Handle trigram similarity for single and multiple words
                if len(words) == 1:
                    word_by_word_content = word_by_word_content.annotate(
                        trigram_similarity_title=TrigramSimilarity('title', words[0]),
                        trigram_similarity_content=TrigramSimilarity('content', words[0])
                    )
                else:
                    word_by_word_content = word_by_word_content.annotate(
                        trigram_similarity_title=Greatest(*[
                            TrigramSimilarity('title', word) for word in words
                        ]),
                        trigram_similarity_content=Greatest(*[
                            TrigramSimilarity('content', word) for word in words
                        ])
                    )

                relevant_content = word_by_word_content.annotate(
                    combined_rank=ExpressionWrapper(
                        F('search_rank') * 2 +
                        F('title_rank') * 3 +
                        F('content_rank') * 1.5 +
                        Greatest(F('trigram_similarity_title') * 2, F('trigram_similarity_content')),
                        output_field=FloatField()
                    )
                ).filter(
                    combined_rank__gt=0.01  # Apply minimum rank threshold
                ).order_by('-combined_rank').only('id', 'title', 'content')

                word_found_results = relevant_content.count()
                logger.info(f"Word-by-word search found {word_found_results} results")

            # Final filtering and limiting to top 5 results
            results = relevant_content.filter(combined_rank__gt=0.01)[:5]
            logger.info(f"Returning top {len(results)} results")

            # Log the titles of the results for debugging
            for result in results:
                logger.info(
                    f"Result: {result.title} (Combined Rank: {result.combined_rank:.4f}, "
                    f"Search Rank: {result.search_rank:.4f}, Title Rank: {result.title_rank:.4f}, "
                    f"Content Rank: {result.content_rank:.4f}, "
                    f"Trigram Sim Title: {result.trigram_similarity_title:.4f}, "
                    f"Trigram Sim Content: {result.trigram_similarity_content:.4f})"
                )

            # Cache the results for future identical queries
            cache.set(cache_key, list(results), timeout=60*5)  # Cache for 5 minutes

            return list(results)

        except Exception as e:
            logger.error(f"Error during search_relevant_content: {e}", exc_info=True)
            return []

def gpt_assistant(prompt: str, prompt_type: str = 'create', model_name: str = '4o-mini') -> dict:
    """
    Convenience function to generate a response using the GPTAssistant class.

    Args:
        prompt (str): The user input prompt.
        prompt_type (str): The type of prompt (default is 'create').
        model_name (str): The name of the AI model to use.

    Returns:
        dict: The generated response from the assistant.
    """
    assistant = GPTAssistant(model_name=model_name)
    return assistant.generate_response(prompt)


