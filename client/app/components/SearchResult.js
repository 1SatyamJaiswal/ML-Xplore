export default function SearchResult({ result }) {
  return (
    <div className="mb-4 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <a 
        href={result.url} 
        target="_blank" 
        rel="noopener noreferrer" 
        className="block"
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
      </a>
    </div>
  );
}