import { getCurrentUser, fetchAuthSession } from 'aws-amplify/auth';


const getUserDetails = async () => {
    let output = await Promise.all([getCurrentUser(), fetchAuthSession()]).then((res) => {
        let merged = { ...res[0], ...res[1] };
        return merged;
    });
    return output;
}

const getUserInfo = async () => {
    let output = await getUserDetails();
    return {
        id: output.identityId,
        email: output.tokens.idToken.payload["email"], 
        accessToken: output.tokens.accessToken.toString(), 
        idToken: output.tokens.idToken.toString()
    };
}

const extractS3BucketAndKey = (url) => {
    const awsS3Pattern = /https:\/\/s3\.([^\/]+)\/([^\/]+)\/(.+)/;
    const match = url.match(awsS3Pattern);
    if (match) {
        return {
            Bucket: match[2],
            Key: match[3]
        };
    } else {
        return null;
    }
}

export {
    getUserDetails,
    getUserInfo,
    extractS3BucketAndKey
};