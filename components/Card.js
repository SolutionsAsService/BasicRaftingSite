const Card = ({ name, yearsExperience, favoriteRapids, description }) => {
    return (
      <div className="bg-white p-4 shadow-md rounded-xl">
        <h2 className="text-xl font-semibold">{name}</h2>
        <p className="text-gray-600">Years of Experience: {yearsExperience}</p>
        <p className="text-gray-600">Favorite Rapids: {favoriteRapids}</p>
        <p className="text-gray-500">{description}</p>
      </div>
    );
  };
  
  export default Card;
