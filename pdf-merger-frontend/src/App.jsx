import Header from "./components/Header";
import FileUpload from "./components/FileUpload";
import "./styles/App.css";

function App() {
    return (
        <div className="app-container">
            <Header />
            <FileUpload />
        </div>
    );
}

export default App;