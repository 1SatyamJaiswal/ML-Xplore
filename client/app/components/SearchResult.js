import axios from "axios";
import Cookies from "js-cookie";

export default function SearchResult({ result, id }) {
  const handleClick = async () => {
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/route`,
        {
          user_id: id,
          resource_url: result.url,
        },
        {
          headers: {
            Authorization: `Bearer ${Cookies.get("token")}`,
          },
        }
      );

      window.open(result.url, "_blank");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <li
      key={result.url}
      onClick={handleClick}
      className="mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow"
    >
      <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-400 hover:underline">
        {result.title}
      </h3>
      <p className="text-gray-600 dark:text-gray-300 mt-1">
        {result.description}
      </p>
      <div className="flex items-center mt-2">
        <span className="text-sm text-gray-500 dark:text-gray-400 mr-2">
          {result.category}
        </span>
        <span className="text-sm text-gray-500 dark:text-gray-400 truncate">
          {result.url}
        </span>
      </div>
    </li>
  );
}
