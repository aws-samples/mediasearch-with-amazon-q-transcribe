import React, { useState } from 'react';
import { Grid, Button, Textarea, SpaceBetween , Spinner} from "@cloudscape-design/components";

const ChatInteractionPanel = ({callback, loading }) => {
    const [value, setValue] = useState("");
    return (<Grid gridDefinition={[{ colspan: 11 }, { colspan: 1 }]} >
        <Textarea placeholder="Enter a prompt"
            disabled={loading}
            rows={2}
            onChange={({ detail }) => setValue(detail.value)}
            value={value}
        />
        <SpaceBetween direction="horizontal" size="l">
            { 
                loading && <Spinner size="large" />
            }
            {
            !loading && <Button iconName="caret-right-filled" iconAlign="right" onClick={() => {if(value !==""){callback(value); setValue("")} }}></Button>
            }
            
        </SpaceBetween>
    </Grid>)

}

export default ChatInteractionPanel;