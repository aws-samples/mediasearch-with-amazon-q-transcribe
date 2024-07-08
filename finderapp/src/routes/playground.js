import React, { useEffect } from 'react';
import { withAuthenticator, useAuthenticator } from '@aws-amplify/ui-react';
import { ContentLayout, Header } from '@cloudscape-design/components';
import Layout from "../layout";
import * as Util from "../common/utility";
import PortalBackend from '../common/api';

import Chat from "./component/chat";
const SSO_IDC_VALUE = "QBUSINESS_SSO_IDC"
const Playground = () => {
    const portalTitle = "Mediasearch Q Business";
    const { signOut } = useAuthenticator((context) => [context.signOut]);
    const [ssoidc, setSsoidc] = React.useState(null)
    const [userInfo, setUserInfo] = React.useState(null);

    useEffect(() => {
        try {
            const init = async () => {
                try {
                    let data = await Util.getUserInfo();
                    try {
                        if (!localStorage.getItem(SSO_IDC_VALUE)) {
                            let tokenData = await PortalBackend.auth.getIdcToken(data.idToken);
                            delete tokenData["ResponseMetadata"];
                            delete tokenData["scope"];
                            delete tokenData["issuedTokenType"];
                            delete tokenData["tokenType"];
                            tokenData["generatedAt"] = Date.now();
                            localStorage.setItem(SSO_IDC_VALUE, JSON.stringify(tokenData))
                            setSsoidc(JSON.parse(JSON.stringify(tokenData)))
                        }
                        else {
                            let idcValue = JSON.parse(localStorage.getItem(SSO_IDC_VALUE))
                            if((Date.now() - idcValue["generatedAt"]) > idcValue["expiresIn"]*1000)
                                onSignOut()
                            else
                                setSsoidc(idcValue)
                        }
                    } catch (e) {
                        localStorage.removeItem(SSO_IDC_VALUE);
                        signOut()
                    }
                    setUserInfo(data);
                } catch (err) {
                    console.log(err);
                }
            }
            init();
        } catch (e) {
            signOut()
        }
    }, []);

    const onSignOut = () => {
        localStorage.removeItem(SSO_IDC_VALUE);
        signOut()
    }
    return (
        <Layout key="applicant_component">
            <ContentLayout
                header={<Header
                    variant="h1"
                >{portalTitle}</Header>}>
                <Chat userinfo={userInfo} signOut={onSignOut} ssoidc={ssoidc} />
            </ContentLayout></Layout>
    )
}
export default withAuthenticator(Playground);