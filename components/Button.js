const Button = ({ label, onClick }) => {
    return (
      <button
        onClick={onClick}
        className="bg-blue-500 text-white px-6 py-2 rounded-lg shadow-md hover:bg-blue-600 transition-all"
      >
        {label}
      </button>
    );
  };
  
  export default Button;
