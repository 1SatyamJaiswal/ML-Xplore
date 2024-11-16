"use client";
import { useEffect, useState } from "react";
import SearchBar from "./components/SearchBar";
import SearchResult from "./components/SearchResult";
import axios from "axios";
import Navbar from "./components/Navbar";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { Content } from "next/font/google";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [email, setEmail] = useState("");
  const [id, setId] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [search, setSearch] = useState(false);
  const router = useRouter();

  // Fetch search results only when the query is valid
  const handleSearch = async (query) => {
    if (!query) {
      setSearchResults([]); // Clear results if the query is empty
      fetchRecommendations(id);
      setSearch(false);
      return;
    }

    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/search?query=${query}`
      );
      setSearchResults(response.data);
      setSearch(true);
    } catch (error) {
      console.error("Error fetching search results:", error);
      setSearchResults([]); // Handle error gracefully by clearing results
    }
  };

  useEffect(() => {
    const token = Cookies.get("token");
    if (token) {
      const user = Cookies.get("user");
      const user_info = user.split(",");
      setEmail(user_info[1]);
      setId(user_info[0]);

      fetchRecommendations(user_info[0]);
    } else {
      router.push("/login"); // Redirect to login if no token is found
    }
  }, []); // Empty dependency array means this effect runs only once on mount

  const fetchRecommendations = async (id) => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/resources`, 
        {
          params: {
            user_id: id,  // Pass user_id as a query parameter
          },
          headers: {
            Authorization: `Bearer ${Cookies.get("token")}`,
            'Content-Type': 'application/json',  // Correct header name
          },
        }
      );
      setSearchResults(response.data);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      setSearchResults([]); // Handle error gracefully by clearing results
    }
  };  

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-black dark:text-white transition-colors duration-300">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <h1 className="text-4xl font-bold text-center mb-8 dark:text-white">
            ML-Xplore
          </h1>

          <div className="mb-8">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              onSearch={handleSearch}
            />
          </div>

          {searchResults.length > 0 && (
            <div className="mt-6">
              <p className="text-gray-600 dark:text-gray-300 mb-4">
                {search ? `Search Results ${searchResults.length} found` : "Recommendations"}
              </p>
              <ul>
                {searchResults.map((result) => (
                  <SearchResult key={result.url} result={result} id={id} />
                ))}
              </ul>
            </div>
          )}

          {searchQuery && searchResults.length === 0 && (
            <div className="text-center text-gray-600 dark:text-gray-300">
              No results found for "{searchQuery}"
            </div>
          )}
        </div>
      </div>
    </>
  );
}
