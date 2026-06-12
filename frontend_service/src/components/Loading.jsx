const Loading = ({ message = "Đang tải..." }) => {
  return (
    <div className="loading">
      <div className="loading-spinner"></div>
      <p>{message}</p>
    </div>
  );
};

export default Loading;