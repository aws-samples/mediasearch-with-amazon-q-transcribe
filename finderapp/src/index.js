import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from "react-router-dom";
import { Amplify } from 'aws-amplify';
import App from './App';
import reportWebVitals from './reportWebVitals';
import "@cloudscape-design/global-styles/index.css"

Amplify.configure(window.aws_config);

window.audioSeeker = () => {
  let val = JSON.parse(window.localStorage.getItem('audioSeeker'))
  for (let i = 0; i < val.length; i++) {
    let audio = document.getElementById(val[i].key)
    try{
      audio.currentTime = val[i].value
    }catch(e){
      console.log(e)
    }
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
      <BrowserRouter>
          <App />
      </BrowserRouter>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();