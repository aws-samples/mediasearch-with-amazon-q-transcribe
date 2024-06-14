import { post } from 'aws-amplify/api';

const API_NAME = "qbusiness_webapp_api"
const PortalBackend = {
    auth : {
        preSigned : async (data,idToken) => {
            let apipath = "/gets3presignedurl";
            let obj = {
                apiName: `${API_NAME}`,
                path: `${apipath}`,
                options: {
                    headers: {
                        authorization: `${idToken}`
                    },                     
                    body: data 
                }
            }
            const restOperation = post(obj)
            const { body } = await restOperation.response;
            const response = await body.json();
            return response;
        },
        
        getIdcToken: async(idToken) => {
            let apipath = "/getIdcToken";
            let obj = {
                apiName: `${API_NAME}`,
                path: `${apipath}`,
                options: {
                    headers: {
                        authorization: `${idToken}`
                    }
                }
            }
            const restOperation = post(obj)
            const { body } = await restOperation.response;
            const response = await body.json();
            return response;
        },


        query: async (data,idToken) => {
            let apipath = "/query";
            let obj = {
                apiName: `${API_NAME}`,
                path: `${apipath}`,
                options: {
                    headers: {
                        authorization: `${idToken}`
                    },                
                    body: data 
                }
            }
            const restOperation = post(obj)
            const { body } = await restOperation.response;
            const response = await body.json();
            return response;
        },
    
        list: async (data,idToken) => {
            let apipath = "/list";
            let obj = {
                apiName: `${API_NAME}`,
                path: `${apipath}`,
                options: {
                    headers: {
                        authorization: `${idToken}`
                    }, 
                    body: data 
                }
            }
            const restOperation = post(obj)
            const { body } = await restOperation.response;
            const response = await body.json();
            return response;
        },
    }        
}

export default PortalBackend;