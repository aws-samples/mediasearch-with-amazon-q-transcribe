import React, { useEffect } from 'react';
import { Button, SpaceBetween } from "@cloudscape-design/components";
import '../layout/style.css'
const Home = () => {
    useEffect(() => {
        document.body.className = "home_body";
      }, []);
    return (
        <div className="home_center">
            <SpaceBetween size="xl">
                <span className="home_title">Mediasearch Q Business</span>
                <Button href='/playground'>Get Started</Button>
            </SpaceBetween>
        </div>)
}
export default Home;