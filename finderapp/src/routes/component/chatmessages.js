import React, { useState, useEffect } from 'react';
import { Container, SpaceBetween, ExpandableSection, Grid, Popover } from "@cloudscape-design/components";

const ChatMessages = ({ data }) => {
    const [chatMessages, setChatMessages] = useState(null);

    useEffect(() => {
        if(data.length > 0){
            let modifiedData = processData(data);
            setChatMessages(modifiedData);
        }else{
            setChatMessages(null);
        }
    }, [data]);

    const generateCitation = (num) => {
        return `<span class="citation_pointer">${num}</span>`
    }
    const generateMessageWithCitation = ( text, textCitation ) =>{
        let start = 0;
        let splitText = []
        for (const [key, value] of Object.entries(textCitation)) {
            let end = parseInt(key);
            let tempText = text.slice(start,end);
            for(let num of value){
                tempText += generateCitation(num)
            }
            splitText.push(tempText)
            start = end + 1;
          }
          splitText.push(text.slice(start))
        return splitText.join(" ");
    }

    const processData = (data) => {
        let newData = [];
        let audioval = []
        for (let message of data) {
            if(message.type === "SYSTEM" && message.sourceAttribution && message.sourceAttribution.length > 0){
                message['source'] = []
                let counter = 1;
                let textSegment = {}

                for (let source of message.sourceAttribution) {
                    let citationNumber = source.citationNumber || counter++
                    let match = (/\[([^\]]*)\]/g).exec(source.snippet)
                    let startTime = 0;
                    let videoId = "";
                    let isExternal = source.url.includes("youtube")
                    let audioPlayerId = `audio_${message.messageId}_${citationNumber}`
                    try {
                        startTime = parseInt(match[1]);
                    } catch (e) { }
                    
                    if (isExternal) {
                        let videoIdMatch = (/v=([a-zA-Z0-9_-]+)/gm).exec(source.url);
                        if (videoIdMatch) {
                            videoId = videoIdMatch[1];
                        }
                    }

                    if (!isExternal)
                        audioval.push({ key: audioPlayerId, value: startTime })

                    
                    for( let textSeg of source.textMessageSegments){
                        if(textSegment[textSeg.endOffset])
                            textSegment[textSeg.endOffset].push(source.citationNumber)
                        else
                            textSegment[textSeg.endOffset] = [source.citationNumber]
                    }
                        
                    message['source'].push({
                        citationNumber: citationNumber,
                        title: source.title,
                        snippet: source.snippet, //.replace(/\[.*?\]/g, '').replace(/\\/g, ''),
                        url: source.url,
                        isExternal: isExternal,
                        videoId: videoId,
                        startTime: startTime,
                        audioPlayerId: audioPlayerId,
                        isVideo: source.isVideo
                    })
                }
                message['body'] = generateMessageWithCitation(message['body'], textSegment);
                delete message['sourceAttribution']
            }
            newData.push(message);
        }
        window.localStorage.setItem("audioSeeker", JSON.stringify(audioval))
        return newData;
    }

    const renderPlayer = (source) => {
        if (source.url !== "") {
            if (source.isExternal) {
                return (<iframe
                    width="300"
                    src={`https://www.youtube.com/embed/${source.videoId}?start=${source.startTime}`}
                    title="YouTube video player"
                    frameBorder="0"></iframe>
                )
            } else {
                if(source.isVideo){
                    return(<video
                        key='audoiElem'
                        preload="true"
                        width="320" height="240"
                        className="source_audio"
                        id={source.audioPlayerId}
                        controls
                        src={source.url} > Your browser does not support the <code>audio</code> element.
                    </video>)
                }else{
                    return(<audio
                        key='audoiElem'
                        preload="true"
                        className="source_audio"
                        id={source.audioPlayerId}
                        controls
                        src={source.url} > Your browser does not support the <code>audio</code> element.
                    </audio>)
                }
                
            }

        } else {
            return null;
        }
    }

    const renderSource = (message) => {
        let component = [];
        if (message.source && message.source.length > 0) {
            let sourcesComponent = []
            for (let source of message.source) {
                sourcesComponent.push(
                    <SpaceBetween key={`citation_${source.citationNumber}`} size="xl">
                        <Grid key={`citation_row${source.citationNumber}`}
                            gridDefinition={[{ colspan: 7 }, { colspan: 5 }]}
                        >
                            
                            <SpaceBetween size='m'>
                                <div className="source_title">
                                    <span className="source_citation">{source.citationNumber}</span>
                                    <span>{source.title}</span>
                                </div>
                                <Popover
                                    dismissButton={false}
                                    size="large"
                                    triggerType="text"
                                    content={source.snippet}
                                >
                                    {(source.snippet.length > 20 ? source.snippet.substring(0, 150) + "..." : source.snippet)}
                                </Popover>
                            </SpaceBetween>

                            { renderPlayer(source) }

                        </Grid><br/>
                    </SpaceBetween>
                )
            }
            component.push(<ExpandableSection key={"expandable_section"} headerText="Sources" onChange={() => {
                window.audioSeeker()
            }}>
                <SpaceBetween>
                    {sourcesComponent}
                </SpaceBetween>
            </ExpandableSection>)
        }
        return component;
    }

    const renderChat = () => {
        let component = [];
        if (chatMessages == null) {
            component.push(
                <SpaceBetween key="nodata_panel" size="l" alignItems="center">
                    <h1>Amazon Q</h1>
                    <h2>Your generative AI assistant for work</h2>
                    <Container key={"chat_load_panel"}>
                        I’m your AI assistant. Enter a prompt to start a conversation. I’ll respond using data from within your organization.
                    </Container>
                </SpaceBetween>
            )
        } else if (chatMessages !== null && chatMessages.length === 0) {
            component = []
        } else {
            let length = chatMessages.length;
            for (let i = length-1; i >=0; i--) {
                let message = chatMessages[i];
                if(message.type === "SYSTEM"){
                    component.push(
                        <SpaceBetween key={`message_${i}`} size="l">
                            <div className='qResponseMessage' dangerouslySetInnerHTML={{ __html: message.body }}></div>
                            {renderSource(message)}
                            <br/>
                        </SpaceBetween>
                    )
                    continue;
                }else if(message.type === "USER"){
                    component.push(
                        <SpaceBetween key={`message_${i}`} size="xl">
                            <span className='qQuestion'>{message.body}</span>
                        </SpaceBetween>
                    )
                    continue;
                }
            }
        }
        return component
    }


    return (
        <Container fitHeight={true} disableHeaderPaddings variant='embedd'>
            {renderChat()}
        </Container>
    )
}

export default ChatMessages