import React from 'react'

const Pagination = ({ streamsPerPage, totalStreams, paginate, currentPage}) => {
  const pageNumbers = [];

  for (let i = 1; i <= Math.ceil(totalStreams / streamsPerPage); i++) {
   pageNumbers.push(i); 
  }

  function renderBtns() {
    return pageNumbers.map((number => {
      if (number === currentPage) {
        return  <li key={number} className="page-item active">
                  <button onClick={() => paginate(number)} className="page-link">
                    {number}
                  </button>
                </li>
      } else {
          return <li key={number} className="page-item">
                    <button onClick={() => paginate(number)} className="page-link">
                      {number}
                    </button>
                  </li>
      }
    }))
  }
  
  return (
    <nav>
      <ul className="pagination">
        {renderBtns() }
      </ul>
    </nav>
  )
}

export default Pagination