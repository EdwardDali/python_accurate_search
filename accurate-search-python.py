import re
from typing import List, Dict, Set, Tuple

class AccurateSearch:
    def __init__(self):
        self.c: List[Dict] = []
        self.t: Dict = {"d": {}, "i": [], "n": {}}

    def add_text(self, id: int, text: str, distance_behind: int = 0):
        if id is None:
            raise ValueError("id is a required parameter")

        cleaned_text = self.cleanup_text(text)
        if len(cleaned_text) > 1000:
            last_space = cleaned_text.rfind(" ", 0, 1000)
            cleaned_text = cleaned_text[:last_space]

        self.c.append({"i": id, "t": cleaned_text})
        words = cleaned_text.split()

        distance_behind = min(distance_behind, 1000)
        distance_behind = int(distance_behind)

        for word in words:
            node = self.t
            for char in word:
                if char not in node["n"]:
                    node["n"][char] = {"d": {}, "i": [], "n": {}}
                node = node["n"][char]

            position = cleaned_text.index(word) + 1
            if distance_behind:
                position += distance_behind

            if id in node["d"]:
                node["d"][id] = min(node["d"][id], position)
            else:
                node["d"][id] = position
                node["i"].append(id)

    def search(self, query: str) -> List[int]:
        results = self.accurate_search(query)
        if not results:
            results = self.accurate_search(self.full_cleanup_text(query))
        if not results:
            results = self.fuzzy_search(query)
        return results

    def accurate_search(self, query: str) -> List[int]:
        words = list(set(self.cleanup_text(query).split()))
        if not self.t:
            raise ValueError("There is no text added to search index")

        results: Dict[int, List[int]] = {}
        visited: Dict[str, Set[int]] = {}

        for word in words:
            if word:
                node = self.t
                for char in word:
                    if char not in node["n"]:
                        break
                    node = node["n"][char]
                else:
                    self._process_word(word, node, results, visited, 4)

        sorted_results = self._sort_results(results)
        return sorted_results

    def fuzzy_search(self, query: str) -> List[int]:
        cleaned_query = self.full_cleanup_text(query)
        for i in range(len(query) - 1, 1, -1):
            cleaned_query += " " + query[:i]
        
        words = [w for w in cleaned_query.split() if len(w) > 1]
        cleaned_query = " ".join(words)
        return self.accurate_search(cleaned_query)

    def suggestions(self, query: str, limit: int) -> List[str]:
        cleaned_query = self.cleanup_text(query)
        suggestions = []

        for item in self.c:
            text = item["t"]
            if len(text) > len(cleaned_query):
                index = text.find(cleaned_query)
                if index >= 0 and (index == 0 or text[index - 1] == " "):
                    space_index = text.find(" ", index + len(cleaned_query) + 1)
                    suggestion = text[index:space_index] if space_index > 0 else text[index:]
                    if len(suggestion) > len(cleaned_query) and suggestion not in suggestions:
                        suggestions.append(suggestion)

            if len(suggestions) >= limit:
                break

        return sorted(suggestions, key=len)

    def remove(self, id: int):
        self.c = [item for item in self.c if item["i"] != id]
        self._remove_from_tree(id, self.t)

    def cleanup_text(self, text: str) -> str:
        text = re.sub(r'<[^>]*>?', ' ', text)
        text = text.lower()
        text = re.sub(r'[`~!%^*()_|=?;:",.<>\{\}\[\]\\\/]', ' ', text)
        return text.strip()

    def full_cleanup_text(self, text: str) -> str:
        text = re.sub(r'<[^>]*>?', ' ', text)
        text = text.lower()
        text = re.sub(r'[^a-z0-9 ]', ' ', text)
        return text.strip()

    def _process_word(self, word: str, node: Dict, results: Dict[int, List[int]], visited: Dict[str, Set[int]], score: int):
        if word not in visited:
            visited[word] = set()

        for id in node["i"]:
            if id not in visited[word]:
                visited[word].add(id)
                if id not in results:
                    results[id] = [100000, 0]
                results[id][0] -= score
                results[id][1] += node["d"][id]

        for char, child_node in node["n"].items():
            self._process_word(word, child_node, results, visited, max(score // 2, 1))

    def _sort_results(self, results: Dict[int, List[int]]) -> List[int]:
        sorted_results = sorted(results.items(), key=lambda x: (x[1][0], x[1][1]))
        return [id for id, _ in sorted_results]

    def _remove_from_tree(self, id: int, node: Dict):
        if id in node["i"]:
            node["i"].remove(id)
        if id in node["d"]:
            del node["d"][id]

        for child_node in node["n"].values():
            self._remove_from_tree(id, child_node)
