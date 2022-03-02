import React, { useState, ReactElement } from 'react';
import { Person, Staffer, Uuid } from '../types';
import useMountEffect from '@restart/hooks/useMountEffect';
import Form from 'react-bootstrap/Form';
import useAutosavingFormData from '../utils/useAutosavingFormData';
import useApiFetch from '../useApiFetch';
import Button from 'react-bootstrap/Button';
import AddStafferModal from './AddStafferModal';
import styles from '../style/components/PersonDetailsPanel.module.scss';
import CouncilMemberDetails from './CouncilMemberDetails';
import StateRepDetails from './StateRepDetails';
import StafferDetails from './StafferDetails';

import { ReactComponent as TrashIcon } from '../assets/trash.svg';

interface Props {
  person: Person;
}

interface FormData {
  notes: string;
}

function formatStaffer(staffer: Staffer) {
  const contactElements: (string | ReactElement | null)[] = [
    ...staffer.officeContacts.map((c) => c.phone),
    staffer.email
  ].filter((item) => !!item);
  if (staffer.twitter) {
    contactElements.push(
      <a href={`https://www.twitter.com/${staffer.twitter}`}>
        @{staffer.twitter}
      </a>
    );
  }
  const contactString =
    contactElements.length == 0
      ? 'No contact info'
      : contactElements.map((item, i) => (
          <>
            {item}
            {i < contactElements.length - 1 && ', '}
          </>
        ));

  return (
    <>
      {staffer.title && <>{staffer.title} - </>}
      {staffer.name} ({contactString})
    </>
  );
}

export default function PersonDetailsPanel(props: Props) {
  const person = props.person;

  const [staffers, setStaffers] = useState<Staffer[] | null>(null);
  const [addStafferModalVisible, setAddStafferModalVisible] =
    useState<boolean>(false);

  const [formData, setFormData, saveStatus] = useAutosavingFormData<FormData>(
    '/api/persons/' + person.id,
    { notes: person.notes }
  );
  const apiFetch = useApiFetch();

  function loadStaffers() {
    apiFetch(`/api/persons/${person.id}/staffers`).then((response) => {
      setStaffers(response);
    });
  }

  useMountEffect(() => {
    if (person.type !== 'STAFFER') {
      loadStaffers();
    }
  });

  function handleNotesChanged(event: any) {
    setFormData({ ...formData, notes: event.target.value });
  }

  function handleAddStaffer(
    name: string,
    title: string,
    phone: string,
    email: string,
    twitter: string
  ) {
    setAddStafferModalVisible(false);
    apiFetch(`/api/persons/${person.id}/staffers`, {
      method: 'POST',
      body: {
        name: name || null,
        title: title || null,
        phone: phone || null,
        email: email || null,
        twitter: twitter || null
      }
    }).then((response) => {
      loadStaffers();
    });
  }

  function handleRemoveStaffer(e: any, id: Uuid) {
    e.preventDefault();
    // TODO: Show a confirmation?
    apiFetch(`/api/persons/-/staffers/` + id, {
      method: 'DELETE'
    }).then((response) => {
      loadStaffers();
    });
  }

  return (
    <Form onSubmit={(e) => e.preventDefault()} className={styles.root}>
      {person.type === 'COUNCIL_MEMBER' && (
        <CouncilMemberDetails person={person} />
      )}
      {person.type === 'SENATOR' && (
        <StateRepDetails
          person={person}
          representativeDetails={person.senator!}
        />
      )}
      {person.type === 'ASSEMBLY_MEMBER' && (
        <StateRepDetails
          person={person}
          representativeDetails={person.assemblyMember!}
        />
      )}
      {person.type === 'STAFFER' ? (
        <StafferDetails person={person} />
      ) : (
        <>
          <div className={styles.label}>
            Staffers:
          </div>
          <div className={styles.content}>
            {staffers &&
              staffers.map((staffer) => (
                <div key={staffer.id} className={styles.staffer}>
                  {formatStaffer(staffer)}
                  &nbsp;
                  <TrashIcon
                    onClick={(e) => handleRemoveStaffer(e, staffer.id)}
                    className={styles.trashIcon}
                  />
                </div>
              ))}
              <Button
              variant="outline-secondary"
              size="sm"
              onClick={() => setAddStafferModalVisible(true)}
              className={`mb-2 d-block ${staffers && staffers.length > 0 && 'mt-2'}`}
            >
              Add staffer
            </Button>
          <AddStafferModal
            show={addStafferModalVisible}
            handleAddStaffer={handleAddStaffer}
            onHide={() => setAddStafferModalVisible(false)}
          />
          </div>{' '}
        </>
      )}
      <div className={styles.label}>Our notes:</div>
      <div className={styles.content}>
        <Form.Control
          as="textarea"
          rows={3}
          size="sm"
          value={formData.notes}
          placeholder="Add our notes about this person"
          onChange={handleNotesChanged}
        />
      </div>
      <div className={styles.label}>{saveStatus}</div>
    </Form>
  );
}
