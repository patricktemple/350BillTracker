import React, { useContext, useState, useEffect, ReactElement } from 'react';
import Accordion from 'react-bootstrap/Accordion';
import AccordionContext from 'react-bootstrap/AccordionContext';

// An Accordion.Body that does not mount its contents to the DOM until the first
// time it is expanded. Useful for delaying unnecessary API calls if they are
// required to render it.
export default function LazyAccordionBody(props: {eventKey?: string, children: ReactElement }) {
  const { activeEventKey } = useContext(AccordionContext);
  const [displayed, setDisplayed] = useState<boolean>(false);

  useEffect(() => {
    if (props.eventKey === activeEventKey && !displayed) {
      setDisplayed(true);
    }
  }, [displayed, setDisplayed, activeEventKey, props.eventKey]);
  return (<Accordion.Body>
    {displayed ? props.children : null}
    </Accordion.Body>);
}