import React from 'react';
import "./style.css";
import ExampleModal from "../modal/ExampleModal";
import TypeModal from "../modal/TypeModal";
import FileUploader from "../file_uploader/FileUploader";
import {TypesDropdown} from "../types_dropdown/TypesDropdown";
import {Categories} from "../categories/Categories";
import Tooltip from "react-bootstrap/Tooltip";
import OverlayTrigger from "react-bootstrap/OverlayTrigger";


class MainPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currentDocType: "bank",
            documentTypes: {
                "bank": "банк",
                "test": "тест"
            },
            imageURL: null,
            loading: false,
            isExampleModalOpen: false,
            isTypeModalOpen: false,
            responseData: {}
        };
    }

    componentDidMount() {
        fetch(`${process.env.REACT_APP_BACKEND}/form_params`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server error');
                }
                return response.json();
            })
            .then(data => {
                // console.log("init data: ", data);
                this.setState({documentTypes: data}); // Set the fetched data to state
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                alert('Сервер не отвечает'); // Display alert for status 500 error
            });
    }


    setFiles = (files) => {
        this.setState({files: files});
    }

    onDocumentTypeChange = (key) => {
        this.setState({currentDocType: key});
        // console.log("choose: ", key);
    }


    openExampleModal = () => {
        // console.log("Modal open");
        this.setState({isExampleModalOpen: true});
    }

    closeExampleModal = () => {
        // console.log("Modal closed");
        this.setState({isExampleModalOpen: false});
    }
    openTypeModal = () => {
        this.setState({isTypeModalOpen: true});
    }


    onNewType = (typeName, categories) => {
        // console.log("onNewType", typeName, categories);
        fetch(`${process.env.REACT_APP_BACKEND}/update_template`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: typeName,
                categories: categories
            })
        })
            .then(response => {
                console.log(response);
                // if (!response.status === 200) {
                //     throw new Error('Network response was not ok');
                // }
                return response.json();
            })
            .then(data => {
                console.log(data)
                if (!(data.status_code===200) && !(typeof data.status_code === 'undefined')) {
                    console.log("here");
                    alert(data.error);
                }
                else {
                    if (data.error){
                        alert(data["error"]);
                    }
                    else {
                        console.log("init data: ", data);
                        console.log("init data: ", data);
                        this.setState({documentTypes: data}); // Set the fetched data to state
                    }
                }
                // Handle the fetched data as needed
            })
            .catch(error => {
                console.error('Error fetching data artmed:', error);
                alert('Error fetching data. Please try again later.');
            })
            .finally(() => {
                this.closeTypeModal(); // Close the modal regardless of success or failure
            });
    };


    closeTypeModal = () => {
        console.log("Modal closed");
        this.setState({isTypeModalOpen: false});
    }

    setResponse = (data) => {
        this.setState({responseData: data})
    }

    sendExample = async (name) => {
        console.log("Sending example");
        this.setState({isExampleModalOpen: false});
        console.log('name=', name);

        const requestData = {name: name};
        this.setState({loading: true});
        console.log(requestData);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND}/handle_example`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json' // Specify content type as JSON
                },
                body: JSON.stringify(requestData) // Convert JSON object to string
            });

            if (!response.ok) {
                throw new Error('Failed to upload file');
            }

            const data = await response.json();
            this.setState({responseData: data});
        } catch (error) {
            alert("Что-то пошло не так, попробуйте заново");
        } finally {
            this.setState({loading: false});
        }
    };


    handleDragOver = (event) => {
        event.preventDefault();
    };

    render() {
        const {loading, isExampleModalOpen, responseData} = this.state;
        const tooltipMargin = {
            marginTop: '-10px', // Adjust the margin as needed
        };
        return (
            <div className="main-page">
                <div className="container mt-4 main-bg">
                    <div className="main-header">
                        <h3>Выберите тип документа:</h3>
                        <OverlayTrigger
                            overlay={<Tooltip style={tooltipMargin}>Добавить тип документа</Tooltip>}
                        >
                            <button
                                className="btn btn-addtype"
                                onClick={this.openTypeModal}
                            >+
                            </button>
                        </OverlayTrigger>
                    </div>
                    <TypesDropdown
                        onChange={this.onDocumentTypeChange}
                        currentDocType={this.state.currentDocType}
                        documentTypes={this.state.documentTypes}
                    />
                    <FileUploader
                        openModal={this.openExampleModal}
                        setFiles={this.setFiles}
                        currentDocType={this.state.currentDocType}
                        documentTypes={this.state.documentTypes}
                        setResponse={this.setResponse}
                        responseData={responseData}
                    />

                    {
                        Object.keys(responseData).length > 0 && (
                            <Categories
                                responseData={responseData}
                                docType={this.state.documentTypes[this.state.currentDocType]}
                            />
                        )
                    }

                    {loading && (
                        <div className="big-center loader"></div>
                    )}
                    <div>
                        <ExampleModal
                            isOpen={isExampleModalOpen}
                            onClose={this.closeExampleModal}
                            onAccept={this.sendExample}
                        >
                            <h2>Modal Content</h2>
                            <p>This is the content of the modal.</p>
                        </ExampleModal>
                        <TypeModal
                            isOpen={this.state.isTypeModalOpen}
                            onClose={this.closeTypeModal}
                            onAccept={this.onNewType}
                        ></TypeModal>
                    </div>
                </div>
            </div>
        );
    }
}

export default MainPage;