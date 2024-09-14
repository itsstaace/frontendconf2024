import React, { useState, useEffect } from "react";
import axios from "axios";
import './App.css';

const App = () => {
  let [reviews, setReviews] = useState([]);
  const [book, setBook] = useState("");
  const [content, setContent] = useState("");

  // Получение отзывов
  useEffect(() => {
    axios.get("http://127.0.0.1:8087/reviews").then((response) => {
      reviews = response.data['reviews'];
      setReviews(response.data['reviews']);
    });
  }, []);

  // Отправка отзыва
  const submitReview = (e) => {
    e.preventDefault();
    const newReview = { book, content };
    
    axios.post("http://127.0.0.1:8087/review", newReview)
      .then((response) => {
        reviews.push(response.data['reviews']);
        setReviews([...reviews]);
        
      });
    
    
  };

  return (
    <div className="container">
      <h1>Отзывы на книги</h1>
      
      <form onSubmit={submitReview}>
        <div>
          <label>Название книги:</label>
          <input
            type="text"
            value={book}
            onChange={(e) => setBook(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Отзыв:</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          />
        </div>
        <button type="submit">Отправить отзыв</button>
      </form>
      
      <h2>Все отзывы</h2>
      <div className="reviews">
        {reviews.map((review) => (
          <div className="review" key={review[0]}>
            <h3>{review[1]}</h3>
            <p dangerouslySetInnerHTML={{ __html: review[2] }} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;
