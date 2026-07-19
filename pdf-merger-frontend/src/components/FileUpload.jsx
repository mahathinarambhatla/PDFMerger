import { useRef, useState } from "react";
import axios from "axios";
import "../styles/Upload.css";

function FileUpload() {

    const [files, setFiles] = useState([]);
    const [downloadUrl, setDownloadUrl] = useState(null);
    const [message, setMessage] = useState("");

    const fileInputRef = useRef(null);


    const handleAddFilesClick = () => {
        fileInputRef.current.click();
    };


    const handleFileChange = (event) => {
        const selectedFiles = Array.from(event.target.files);
    
        const newFiles = selectedFiles.filter((file) => {
            return !files.some(
                (existingFile) =>
                    existingFile.name === file.name &&
                    existingFile.size === file.size
            );
        });
    
        if (newFiles.length !== selectedFiles.length) {
            alert("Duplicate files are not allowed");
        }
    
        setFiles([...files, ...newFiles]);
    
        // reset input so same file can be selected again after removal
        event.target.value = "";
    };


    const handleRemoveFile = (index) => {

        setFiles((previousFiles) =>
            previousFiles.filter((_, i) => i !== index)
        );

    };


    const handleMerge = async () => {


        if (files.length < 2) {
            setMessage("Please select at least 2 PDF files");
            return;
        }


        const formData = new FormData();


        files.forEach((file) => {
            formData.append("files", file);
        });


        try {

            setMessage("Merging PDFs...");


            const response = await axios.post(
                "http://localhost:5000/merge",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                    responseType: "blob",
                }
            );


            // Convert PDF response into downloadable URL

            const pdfBlob = new Blob(
                [response.data],
                {
                    type: "application/pdf",
                }
            );


            const url = window.URL.createObjectURL(pdfBlob);


            setDownloadUrl(url);

            setMessage("PDF merged successfully ✅");


        } catch (error) {

            console.error(
                "Merge failed:",
                error
            );

            setMessage(
                "Failed to merge PDFs"
            );

        }

    };


    return (

        <div>

            <button onClick={handleAddFilesClick}>
                + Add Files
            </button>


            <input
                type="file"
                ref={fileInputRef}
                multiple
                accept="application/pdf"
                onChange={handleFileChange}
                style={{ display: "none" }}
            />


            {
                files.map((file, index) => (

                    <div key={index}>

                        <span>
                            {index + 1}. {file.name}
                        </span>


                        <button 
                            onClick={() => handleRemoveFile(index)}
                        >
                            ❌
                        </button>


                    </div>

                ))
            }



            {
                files.length > 0 && (

                    <button onClick={handleMerge}>
                        Merge PDFs
                    </button>

                )
            }



            {
                message && (

                    <p>
                        {message}
                    </p>

                )
            }



            {
                downloadUrl && (

                    <div>

                        <a
                            href={downloadUrl}
                            download="merged.pdf"
                        >

                            <button>
                                Download Merged PDF
                            </button>

                        </a>

                    </div>

                )
            }


        </div>

    );
}

export default FileUpload;